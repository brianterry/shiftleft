import aws_cdk.aws_s3
from aws_cdk.core import (
    # core,
    Stack,
    RemovalPolicy,
    Duration,
    Tags,
    App,
    )
from aws_cdk import (    
    aws_s3,
    aws_kms,
    aws_iam
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
                               # Uncomment encryption=aws_s3.BucketEncryption.KMS, to enable encryption
                               #encryption=aws_s3.BucketEncryption.KMS,

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
                               block_public_access=aws_cdk.aws_s3.BlockPublicAccess(
                                   # Uncomment block_public_acls=True and remove block_public_acls=False
                                   # block_public_acls=True,
                                   block_public_acls=False,
                                   restrict_public_buckets=True,
                                   block_public_policy=True,
                                   ignore_public_acls=True
                               )
                               )
        # Adds a Tag Name->App, Value->policy-as-code
        for i in [bucket]:
            Tags.of(i).add('App', 'policy-as-code')