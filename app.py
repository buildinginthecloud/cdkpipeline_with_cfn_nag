#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from repository import RepositoryStack
from cdkpipeline import CdkPipelineStack

app = core.App()
RepositoryStack(app, 'SourceRepository')
CdkPipelineStack(app, "CdkPipeline",
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # SECURITY BEST PRACTICE: Use environment variables instead of hardcoded values
    # Uncomment the next line to use AWS CLI configuration:
    # env=core.Environment(
    #     account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    #     region=os.getenv('CDK_DEFAULT_REGION')
    # ),

    # SECURITY WARNING: Never hardcode account IDs or regions in source code
    # Use environment variables, AWS SSM Parameter Store, or AWS Secrets Manager
    # Example removed for security reasons

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    )

app.synth()

