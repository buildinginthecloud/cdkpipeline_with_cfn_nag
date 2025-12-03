from aws_cdk import (
    aws_s3 as s3,
    core as cdk,
)

class BucketStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SECURITY ENHANCEMENT: Create S3 Bucket with security best practices
        # Note: This CDK v1 configuration should be migrated to CDK v2
        # See SECURITY_ANALYSIS.md for migration guide
        
        # Create logging bucket first for access logs
        log_bucket = s3.Bucket(
            self, 'LogBucket',
            # Enable encryption for logs
            encryption=s3.BucketEncryption.S3_MANAGED,
            # Block all public access to logs
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            # Enable versioning for log retention
            versioned=True,
            # Prevent accidental deletion of logs
            removal_policy=cdk.RemovalPolicy.RETAIN
        )
        
        # Create secure S3 Bucket with comprehensive security controls
        s3.Bucket(
            self, 'S3Bucket',
            # SECURITY: Enable server-side encryption (SSE-S3)
            # Consider using SSE-KMS for enhanced key management
            encryption=s3.BucketEncryption.S3_MANAGED,
            
            # SECURITY: Enable versioning to protect against accidental deletion
            # and provide recovery capabilities
            versioned=True,
            
            # SECURITY: Block all public access to prevent data exposure
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            
            # SECURITY: Enable access logging for audit trail
            server_access_logs_bucket=log_bucket,
            server_access_logs_prefix='s3-access-logs/',
            
            # BEST PRACTICE: Add lifecycle rules for cost optimization
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    # Transition to Infrequent Access after 90 days
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=cdk.Duration.days(90)
                        )
                    ],
                    # Clean up old versions after 90 days
                    noncurrent_version_expiration=cdk.Duration.days(90)
                )
            ],
            
            # BEST PRACTICE: Retain bucket on stack deletion to prevent data loss
            removal_policy=cdk.RemovalPolicy.RETAIN
        )

