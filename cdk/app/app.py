import re
from aws_cdk.core import (
    App,
    Environment,
    #Aspects,
)
#from cdk_nag import ( AwsSolutionsChecks, NagSuppressions, NagPackSuppression )
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

#Uncomment to enable Aspects
#Aspects.of(app).add(AwsSolutionsChecks())

#NagSuppressions.add_resource_suppressions_by_path(stack, "/policy-as-code/AutomationAssumeRole/Resource", suppressions=[
#    NagPackSuppression(
#        id='AwsSolutions-IAM4',
#        reason='No need to rotate',
#    )
#])
#NagSuppressions.add_resource_suppressions_by_path(stack, "/policy-as-code/AutomationAssumeRole/Resource", suppressions=[
#    NagPackSuppression(
#        id='AwsSolutions-KMS5',
#        reason='No needed',
#    )
#])

#NagSuppressions.add_resource_suppressions_by_path(stack, "/policy-as-code/Bucket/Key/Resource", suppressions=[
#    NagPackSuppression(
#        id='AwsSolutions-IAM5',
#        reason='Not needex',
#    )
#])
#NagSuppressions.add_resource_suppressions_by_path(stack, "/policy-as-code/Bucket/Resource", suppressions=[
#    NagPackSuppression(
#        id='AwsSolutions-S1',
#        reason='No access logs required for this bucket',
#    )
#])
app.synth()
