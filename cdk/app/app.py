import re
from aws_cdk.core import (
    App,
    Environment,
    Aspects,
)
from cdk_nag import ( AwsSolutionsChecks, NagSuppressions, NagPackSuppression )
import os
import pathlib
from s3_deployment import S3AppStack

app = App()

stack = S3AppStack(app, "policy-as-code",
           env=Environment(
               account=os.environ["CDK_DEFAULT_ACCOUNT"],
               region=os.environ["CDK_DEFAULT_REGION"]
           ),
           description='')
Aspects.of(app).add(AwsSolutionsChecks())
NagSuppressions.add_resource_suppressions_by_path(stack, "/policy-as-code/Bucket/Resource", suppressions=[
    NagPackSuppression(
        id='AwsSolutions-S1',
        reason='No access logs required for this bucket',
    )
])
app.synth()
