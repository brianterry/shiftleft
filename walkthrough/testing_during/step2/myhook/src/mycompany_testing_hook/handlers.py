import logging
from typing import Any, MutableMapping, Optional
import botocore

from cloudformation_cli_python_lib import (
    BaseHookHandlerRequest,
    HandlerErrorCode,
    Hook,
    HookInvocationPoint,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import HookHandlerRequest, TypeConfigurationModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "MyCompany::Testing::Hook"

LOG.setLevel(logging.INFO)

hook = Hook(TYPE_NAME, TypeConfigurationModel)
test_entrypoint = hook.test_entrypoint


def _validate_s3_bucket_encryption(bucket: MutableMapping[str, Any], required_encryption_algorithm: str) -> ProgressEvent:
    status = None
    message = ""
    error_code = None

    if bucket:
        bucket_name = bucket.get("BucketName")

        bucket_encryption = bucket.get("BucketEncryption")
        if bucket_encryption:
            server_side_encryption_rules = bucket_encryption.get("ServerSideEncryptionConfiguration")
            if server_side_encryption_rules:
                for rule in server_side_encryption_rules:
                    bucket_key_enabled = rule.get("BucketKeyEnabled")
                    if bucket_key_enabled:
                        server_side_encryption_by_default = rule.get("ServerSideEncryptionByDefault")

                        encryption_algorithm = server_side_encryption_by_default.get("SSEAlgorithm")
                        kms_key_id = server_side_encryption_by_default.get("KMSMasterKeyID")  # "KMSMasterKeyID" is name of the property for an AWS::S3::Bucket

                        if encryption_algorithm == required_encryption_algorithm:
                            if encryption_algorithm == "aws:kms" and not kms_key_id:
                                status = OperationStatus.FAILED
                                message = f"KMS Key ID not set for bucket with name: f{bucket_name}"
                            else:
                                status = OperationStatus.SUCCESS
                                message = f"Successfully invoked PreCreateHookHandler for AWS::S3::Bucket with name: {bucket_name}"
                        else:
                            status = OperationStatus.FAILED
                            message = f"SSE Encryption Algorithm is incorrect for bucket with name: {bucket_name}"
                    else:
                        status = OperationStatus.FAILED
                        message = f"Bucket key not enabled for bucket with name: {bucket_name}"

                    if status == OperationStatus.FAILED:
                        break
            else:
                status = OperationStatus.FAILED
                message = f"No SSE Encryption configurations for bucket with name: {bucket_name}"
        else:
            status = OperationStatus.FAILED
            message = f"Bucket Encryption not enabled for bucket with name: {bucket_name}"
    else:
        status = OperationStatus.FAILED
        message = "Resource properties for S3 Bucket target model are empty"

    if status == OperationStatus.FAILED:
        error_code = HandlerErrorCode.NonCompliant

    return ProgressEvent(
        status=status,
        message=message,
        errorCode=error_code
    )


def _validate_sqs_queue_encryption(queue: MutableMapping[str, Any]) -> ProgressEvent:
    if not queue:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            message="Resource properties for SQS Queue target model are empty",
            errorCode=HandlerErrorCode.NonCompliant
        )
    queue_name = queue.get("QueueName")

    kms_key_id = queue.get("KmsMasterKeyId")  # "KmsMasterKeyId" is name of the property for an AWS::SQS::Queue
    if not kms_key_id:
        return ProgressEvent(
            status=OperationStatus.FAILED,
            message=f"Server side encryption turned off for queue with name: {queue_name}",
            errorCode=HandlerErrorCode.NonCompliant
        )

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        message=f"Successfully invoked PreCreateHookHandler for targetAWS::SQS::Queue with name: {queue_name}"
    )


@hook.handler(HookInvocationPoint.CREATE_PRE_PROVISION)
def pre_create_handler(
        session: Optional[SessionProxy],
        request: HookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    target_name = request.hookContext.targetName
    if "AWS::S3::Bucket" == target_name:
        return _validate_s3_bucket_encryption(request.hookContext.targetModel.get("resourceProperties"), type_configuration.encryptionAlgorithm)
    elif "AWS::SQS::Queue" == target_name:
        return _validate_sqs_queue_encryption(request.hookContext.targetModel.get("resourceProperties"))
    else:
        raise exceptions.InvalidRequest(f"Unknown target type: {target_name}")



def _validate_bucket_encryption_rules_not_updated(resource_properties, previous_resource_properties) -> ProgressEvent:
    bucket_encryption_configs = resource_properties.get("BucketEncryption", {}).get("ServerSideEncryptionConfiguration", [])
    previous_bucket_encryption_configs = previous_resource_properties.get("BucketEncryption", {}).get("ServerSideEncryptionConfiguration", [])

    if len(bucket_encryption_configs) != len(previous_bucket_encryption_configs):
        return ProgressEvent(
            status=OperationStatus.FAILED,
            message=f"Current number of bucket encryption configs does not match previous. Current has {str(len(bucket_encryption_configs))} configs while previously there were {str(len(previous_bucket_encryption_configs))} configs",
            errorCode=HandlerErrorCode.NonCompliant
        )

    for i in range(len(bucket_encryption_configs)):
        current_encryption_algorithm = bucket_encryption_configs[i].get("ServerSideEncryptionByDefault", {}).get("SSEAlgorithm")
        previous_encryption_algorithm = previous_bucket_encryption_configs[i].get("ServerSideEncryptionByDefault", {}).get("SSEAlgorithm")

        if current_encryption_algorithm != previous_encryption_algorithm:
            return ProgressEvent(
                status=OperationStatus.FAILED,
                message=f"Bucket Encryption algorithm can not be changed once set. The encryption algorithm was changed to {current_encryption_algorithm} from {previous_encryption_algorithm}.",
                errorCode=HandlerErrorCode.NonCompliant
            )

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        message="Successfully invoked PreUpdateHookHandler for target: AWS::SQS::Queue"
    )

def _validate_queue_encryption_not_disabled(resource_properties, previous_resource_properties) -> ProgressEvent:
    if previous_resource_properties.get("KmsMasterKeyId") and not resource_properties.get("KmsMasterKeyId"):
        return ProgressEvent(
            status=OperationStatus.FAILED,
            errorCode=HandlerErrorCode.NonCompliant,
            message="Queue encryption can not be disable",
        )
    else:
        return ProgressEvent(
            status=OperationStatus.SUCCESS
        )


@hook.handler(HookInvocationPoint.UPDATE_PRE_PROVISION)
def pre_update_handler(
        session: Optional[SessionProxy],
        request: BaseHookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: MutableMapping[str, Any]
) -> ProgressEvent:
    target_name = request.hookContext.targetName
    if "AWS::S3::Bucket" == target_name:
        return _validate_s3_bucket_encryption(request.hookContext.targetModel.get("resourceProperties"), type_configuration.encryptionAlgorithm)
        
    elif "AWS::SQS::Queue" == target_name:
        resource_properties = request.hookContext.targetModel.get("resourceProperties")
        previous_resource_properties = request.hookContext.targetModel.get("previousResourceProperties")

        return _validate_queue_encryption_not_disabled(resource_properties, previous_resource_properties)
    else:
        raise exceptions.InvalidRequest(f"Unknown target type: {target_name}")

