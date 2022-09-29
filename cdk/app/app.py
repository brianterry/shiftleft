from aws_cdk.core import (
    App,
    Environment,
    Aspects,
)
from cdk_nag import ( AwsSolutionsChecks )
import os
import pathlib
from s3_deployment import S3AppStack

app = App()

S3AppStack(app, "policy-as-code",
           env=Environment(
               account=os.environ["CDK_DEFAULT_ACCOUNT"],
               region=os.environ["CDK_DEFAULT_REGION"]
           ),
           description='')
Aspects.of(app).add(AwsSolutionsChecks())
app.synth()
