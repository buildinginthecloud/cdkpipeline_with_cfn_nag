
from aws_cdk import (
    aws_codecommit as codecommit,
    core as cdk
)

class RepositoryStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create codecommit repository to store files
        # SECURITY NOTE: CodeCommit encrypts repositories at rest by default using AWS-managed keys
        # For enhanced security, consider using customer-managed KMS keys (requires CDK v2)
        codecommit.Repository(
            self, 'Repository',
            repository_name='cdkpipeline_with_cfn_nag',
            description='Repository for CDK pipeline with CFN Nag'
        )