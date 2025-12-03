# CDK v2 Migration Examples

This document provides concrete examples for migrating this repository from AWS CDK v1 to CDK v2.

## Table of Contents
1. [Dependencies](#dependencies)
2. [app.py Migration](#apppy-migration)
3. [bucket_stack.py Migration](#bucket_stackpy-migration)
4. [repository.py Migration](#repositorypy-migration)
5. [cdkpipeline.py Migration](#cdkpipelinepy-migration)
6. [Testing After Migration](#testing-after-migration)

---

## Dependencies

### Before (requirements.txt - CDK v1)
```txt
aws_cdk.aws_codecommit==1.121.0
aws_cdk.pipelines==1.121.0
aws_cdk.aws_s3==1.121.0
-e .
```

### After (requirements.txt - CDK v2)
```txt
aws-cdk-lib>=2.178.0
constructs>=10.0.0
-e .
```

### Before (setup.py - CDK v1)
```python
install_requires=[
    "aws-cdk.core==1.121.0",
],
python_requires=">=3.6",
```

### After (setup.py - CDK v2)
```python
install_requires=[
    "aws-cdk-lib>=2.178.0",
    "constructs>=10.0.0",
],
python_requires=">=3.9",
```

---

## app.py Migration

### Before (CDK v1)
```python
#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import core

from repository import RepositoryStack
from cdkpipeline import CdkPipelineStack

app = core.App()
RepositoryStack(app, 'SourceRepository')
CdkPipelineStack(app, "CdkPipeline")

app.synth()
```

### After (CDK v2)
```python
#!/usr/bin/env python3
import os

from aws_cdk import (
    App,
    Environment,
)

from repository import RepositoryStack
from cdkpipeline import CdkPipelineStack

app = App()
RepositoryStack(app, 'SourceRepository')
CdkPipelineStack(
    app, 
    "CdkPipeline",
    # Use environment variables for account/region
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()
```

**Key Changes:**
- `from aws_cdk import core` → `from aws_cdk import App, Environment`
- `core.App()` → `App()`
- `core.Environment` → `Environment`
- Single CDK library import instead of multiple packages

---

## bucket_stack.py Migration

### Before (CDK v1)
```python
from aws_cdk import (
    aws_s3 as s3,
    core as cdk,
)

class BucketStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(self, 'S3Bucket')
```

### After (CDK v2)
```python
from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
)
from aws_cdk import aws_s3 as s3
from constructs import Construct

class BucketStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create logging bucket for access logs
        log_bucket = s3.Bucket(
            self, 'LogBucket',
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Create secure S3 Bucket with security best practices
        s3.Bucket(
            self, 'S3Bucket',
            # Encryption with AWS-managed keys
            encryption=s3.BucketEncryption.S3_MANAGED,
            
            # Enable versioning for data protection
            versioned=True,
            
            # Block all public access
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            
            # Enable access logging for audit trail
            server_access_logs_bucket=log_bucket,
            server_access_logs_prefix='s3-access-logs/',
            
            # Lifecycle rules for cost optimization
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(90)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(180)
                        )
                    ],
                    noncurrent_version_transitions=[
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30)
                        )
                    ],
                    noncurrent_version_expiration=Duration.days(90)
                )
            ],
            
            # Prevent accidental deletion
            removal_policy=RemovalPolicy.RETAIN
        )
```

**Key Changes:**
- `cdk.Stack` → `Stack` (imported from `aws_cdk`)
- `cdk.Construct` → `Construct` (imported from `constructs` package)
- `aws_s3` now imported from `aws_cdk` package
- `cdk.Duration` → `Duration`
- `cdk.RemovalPolicy` → `RemovalPolicy`
- Added comprehensive security configurations

---

## repository.py Migration

### Before (CDK v1)
```python
from aws_cdk import (
    aws_codecommit as codecommit,
    core as cdk
)

class RepositoryStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        codecommit.Repository(
            self, 'Repository',
            repository_name='cdkpipeline_with_cfn_nag',
            description='Repository for CDK pipeline with CFN Nag'
        )
```

### After (CDK v2)
```python
from aws_cdk import Stack
from aws_cdk import aws_codecommit as codecommit
from constructs import Construct

class RepositoryStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CodeCommit repository
        # Note: CodeCommit encrypts at rest by default with AWS-managed keys
        codecommit.Repository(
            self, 'Repository',
            repository_name='cdkpipeline_with_cfn_nag',
            description='Repository for CDK pipeline with CFN Nag'
        )
```

**Key Changes:**
- `core as cdk` → Import `Stack` directly
- `cdk.Stack` → `Stack`
- `cdk.Construct` → `Construct` from `constructs`
- `aws_codecommit` imported from `aws_cdk`

---

## cdkpipeline.py Migration

### Before (CDK v1)
```python
import os
from aws_cdk import (
    aws_codecommit as codecommit,
    pipelines,
    core as cdk
)
from s3bucket.bucket_stack import BucketStack

class S3BucketStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3_bucket = BucketStack(self, "S3BucketStack")

class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = codecommit.Repository.from_repository_name(
            self, 'pipeline_repository', 'cdkpipeline_with_cfn_nag'
        )

        pipeline = pipelines.CodePipeline(
            self, "CDKPipeline", 
            pipeline_name="CDKPipeline",
            synth=pipelines.ShellStep("Synth",
                input=pipelines.CodePipelineSource.code_commit(repository, "main"),
                commands=[
                    "npm install -g aws-cdk",
                    "gem install cfn-nag",
                    "pip install -r requirements.txt",
                    "cdk synth",
                    "mkdir ./cfnnag_output",
                    "for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cp $template ./cfnnag_output; done",
                    "cfn_nag_scan --input-path ./cfnnag_output",
                ]
            )
        )

        s3Deplpoy = pipeline.add_stage(
            S3BucketStage(self, 'S3BucketStage')
        )
```

### After (CDK v2)
```python
import os
from aws_cdk import (
    Stack,
    Stage,
    Environment,
)
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import pipelines
from constructs import Construct

from s3bucket.bucket_stack import BucketStack

class S3BucketStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3_bucket = BucketStack(self, "S3BucketStack")

class CdkPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference existing CodeCommit repository
        repository = codecommit.Repository.from_repository_name(
            self, 'pipeline_repository', 'cdkpipeline_with_cfn_nag'
        )

        # Create CDK Pipeline with security scanning
        pipeline = pipelines.CodePipeline(
            self, "CDKPipeline", 
            pipeline_name="CDKPipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.code_commit(repository, "main"),
                commands=[
                    # Install CDK v2
                    "npm install -g aws-cdk",
                    # Install cfn_nag for security scanning
                    "gem install cfn-nag",
                    # Install Python dependencies
                    "pip install -r requirements.txt",
                    # Synthesize CDK app
                    "cdk synth",
                    # Prepare templates for scanning
                    "mkdir ./cfnnag_output",
                    "for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cp $template ./cfnnag_output; done",
                    # Run security scan
                    "cfn_nag_scan --input-path ./cfnnag_output",
                ]
            )
        )

        # Deploy S3 bucket stage with environment configuration
        s3_deploy = pipeline.add_stage(
            S3BucketStage(
                self, 
                'S3BucketStage',
                env=Environment(
                    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                    region=os.getenv('CDK_DEFAULT_REGION')
                )
            )
        )
```

**Key Changes:**
- `cdk.Stack` → `Stack`
- `cdk.Stage` → `Stage`
- `cdk.Construct` → `Construct` from `constructs`
- `cdk.Environment` → `Environment`
- All AWS service imports from `aws_cdk` package
- Added explicit environment configuration
- Fixed typo: `s3Deplpoy` → `s3_deploy`

---

## Testing After Migration

### Step 1: Install Dependencies
```bash
# Create/activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat

# Install CDK v2 dependencies
pip install -r requirements.txt

# Verify installation
cdk --version  # Should show 2.x.x
```

### Step 2: Synthesize CloudFormation
```bash
# Synthesize to check for errors
cdk synth

# Should output CloudFormation templates without errors
```

### Step 3: Run Security Scanning
```bash
# Install cfn_nag (requires Ruby)
gem install cfn-nag

# Scan synthesized templates
mkdir ./cfnnag_output
for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do 
    cp $template ./cfnnag_output
done
cfn_nag_scan --input-path ./cfnnag_output
```

### Step 4: Compare Templates (Diff)
```bash
# Compare CDK v1 vs CDK v2 templates
cdk diff

# Review differences carefully before deploying
```

### Step 5: Deploy to Test Environment
```bash
# Set environment variables
export CDK_DEFAULT_ACCOUNT="your-account-id"
export CDK_DEFAULT_REGION="your-region"

# Deploy to test/dev environment first
cdk deploy --all --profile test-profile

# Verify deployed resources in AWS Console
```

### Step 6: Validate Functionality
- Check that CodeCommit repository is accessible
- Verify CodePipeline is created and functional
- Confirm S3 bucket has all security settings:
  - Encryption enabled
  - Versioning enabled
  - Public access blocked
  - Access logging configured
- Test pipeline by pushing code to repository
- Verify cfn_nag scanning runs in pipeline

### Step 7: Run Tests (if applicable)
```bash
# If you have unit tests
python -m pytest tests/

# Or use cdk test command
cdk test
```

---

## Common Migration Issues and Solutions

### Issue 1: Import Errors
**Error:** `ImportError: cannot import name 'core' from 'aws_cdk'`

**Solution:** Update all imports to use new CDK v2 structure:
- `from aws_cdk import core` → `from aws_cdk import Stack, App, etc.`
- Import `Construct` from `constructs` package

### Issue 2: Type Hints
**Error:** Type checking fails with `cdk.Construct`

**Solution:** Update type hints:
- `scope: cdk.Construct` → `scope: Construct`
- Import: `from constructs import Construct`

### Issue 3: Duration Not Found
**Error:** `AttributeError: module 'aws_cdk.core' has no attribute 'Duration'`

**Solution:** Import Duration directly:
```python
from aws_cdk import Duration
# Use: Duration.days(90)
```

### Issue 4: Context Feature Flags
**Error:** Warning about feature flags in cdk.json

**Solution:** Update `cdk.json` with CDK v2 feature flags:
```json
{
  "app": "python3 app.py",
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true,
    "@aws-cdk/core:target-partitions": ["aws", "aws-cn"],
    "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": true,
    "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": true,
    "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": true,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,
    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": true,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,
    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:enablePartitionLiterals": true,
    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": true,
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "@aws-cdk/core:stackRelativeExports": true
  }
}
```

### Issue 5: Pipeline Changes
**Error:** `pipelines.CodePipeline` API differences

**Solution:** Review CDK v2 pipelines documentation as some properties have changed:
- `synth` now uses `ShellStep` (same in both versions)
- `add_stage` method signature is the same
- Environment handling is more explicit

---

## Rollback Plan

If issues occur after migration:

1. **Backup CDK v1 Code:**
   ```bash
   git checkout -b backup-cdk-v1
   git commit -am "Backup before CDK v2 migration"
   ```

2. **Revert Changes:**
   ```bash
   git checkout main
   git revert <migration-commit-hash>
   ```

3. **Restore Dependencies:**
   ```bash
   # Switch back to CDK v1 in requirements.txt
   pip install -r requirements.txt
   ```

4. **Redeploy Previous Version:**
   ```bash
   cdk deploy --all
   ```

---

## Additional Resources

- **AWS CDK v2 Migration Guide:** https://docs.aws.amazon.com/cdk/v2/guide/migrating-v2.html
- **AWS CDK v2 API Reference:** https://docs.aws.amazon.com/cdk/api/v2/
- **CDK v2 Release Notes:** https://github.com/aws/aws-cdk/releases
- **Migration Tool:** Use `cdk migrate` for automated assistance
- **CDK Patterns:** https://cdkpatterns.com/ (updated for v2)

---

## Support

For migration assistance:
- AWS CDK GitHub Issues: https://github.com/aws/aws-cdk/issues
- AWS CDK Slack: https://cdk.dev/
- AWS Support: If you have AWS Premium Support

---

**Last Updated:** 2025-01-13  
**CDK Version:** v2.178.0+  
**Python Version:** 3.9+
