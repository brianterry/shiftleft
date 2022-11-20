import aws_cdk.aws_s3
from aws_cdk.core import (
    # core,
    Stack,
    RemovalPolicy,
    Duration,
    Tags,
    App
)
from aws_cdk import (
    aws_s3,
    aws_kms,
    aws_iam,
    aws_config
)
from aws_cdk.aws_iam import (
    ManagedPolicy,
    PolicyStatement,
    PolicyDocument,
    Role,
    ServicePrincipal
)
from aws_cdk.aws_config import (
    ManagedRule,
    RuleScope,
    ResourceType,
    CfnRemediationConfiguration,
)
from aws_cdk.aws_iam import (
    ManagedPolicy,
    PolicyStatement,
    PolicyDocument,
    Role,
    ServicePrincipal
)

import os


class S3AppStack(Stack):
    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        # Create our Bucket
        bucket = aws_s3.Bucket(self, 'Bucket',
                               removal_policy=RemovalPolicy.DESTROY,
                               auto_delete_objects=False,
                               versioned=True,
                               # Comment out the following to disable public read access.
                               public_read_access=True,
                               # Uncommment the following to enable encryption.
                               #encryption=aws_s3.BucketEncryption.S3_MANAGED,
                               
                               # Comment the encryption=aws_s3.BucketEncryption.S3_MANAGED line
                               # Uncomment encryption=aws_s3.BucketEncryption.KMS and encryption=aws_s3.BucketEncryption.KMS, to enable encryption
                               #encryption=aws_s3.BucketEncryption.KMS,
                               #bucket_key_enabled= True,
                               
                               # Uncomment to clear AwsSolutions-S2 error
                               #block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL, 
                               
                               # Uncomment to to clear AwsSolutions-S10 error
                               #enforce_ssl=True,


                               lifecycle_rules=[
                                   aws_s3.LifecycleRule(
                                       enabled=True,
                                       # expiration=core.Duration.days(90),
                                       noncurrent_version_expiration=Duration.days(
                                           180),
                                       abort_incomplete_multipart_upload_after=Duration.days(
                                           5),
                                       transitions=[
                                           aws_s3.Transition(
                                               storage_class=aws_s3.StorageClass.INFREQUENT_ACCESS,
                                               transition_after=Duration.days(
                                                   60)
                                           )
                                       ],
                                       noncurrent_version_transitions=[
                                           aws_s3.NoncurrentVersionTransition(
                                               storage_class=aws_s3.StorageClass.INFREQUENT_ACCESS,
                                               transition_after=Duration.days(
                                                   31)
                                           )
                                       ]
                                   )
                               ],
                               )
        # Adds a Tag Name->App, Value->policy-as-code
        for i in [bucket]:
            Tags.of(i).add('App', 'policy-as-code')

        s3_config_rule = aws_config.ManagedRule(self, 'AwsConfigRuleS3',
                                                config_rule_name='S3PublicAccessSettings',
                                                identifier=aws_config.ManagedRuleIdentifiers.S3_BUCKET_PUBLIC_READ_PROHIBITED,
                                                description='Checks that your Amazon S3 buckets do not allow public read access. The rule checks the Block Public Access settings, the bucket policy, and the bucket access control list (ACL).',
                                                maximum_execution_frequency=aws_config.MaximumExecutionFrequency.ONE_HOUR,
                                                rule_scope=RuleScope.from_resource(
                                                    ResourceType.S3_BUCKET, bucket.bucket_name)
                                                )
        #####################################################################################################################################################
        #Setting up Remediation [CDK app]  step 2 starts here
        
        #automation_assume_role = aws_iam.Role(self,
        #                                      'AutomationAssumeRole',
        #                                      assumed_by=ServicePrincipal(
        #                                         'ssm.amazonaws.com'),
        #                                      managed_policies=[ManagedPolicy.from_managed_policy_arn(
        #                                          self, 'AmazonSSMAutomation', 'arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole')],
        #                                      inline_policies={
        #                                          "S3FullAccess":
        #                                          PolicyDocument(
        #                                              statements=[PolicyStatement(
        #                                                  actions=["s3:*"], resources=[bucket.bucket_arn])]
        #                                          )
        #                                      }
        #                                      )


        #CfnRemediationConfiguration(self,
        #                            'AwsConfigRemdiationS3',
        #                            config_rule_name=s3_config_rule.config_rule_name,
        #                            target_id='AWS-DisableS3BucketPublicReadWrite',
        #                            target_type='SSM_DOCUMENT',
        #                            automatic=True,
        #                            maximum_automatic_attempts=3,
        #                            retry_attempt_seconds=60,
        #                            parameters={
        #                                'AutomationAssumeRole': {
        #                                    'StaticValue': {
        #                                        'Values': [automation_assume_role.role_arn]
        #                                    }
        #                                },
        #                                'S3BucketName': {
        #                                    'ResourceValue': {
        #                                        'Value': 'RESOURCE_ID'
        #                                    }
        #                                }
        #                            }
        #                            )
        #####################################################################################################################################################
        #Setting up Remediation [CDK app] step 2 ends here