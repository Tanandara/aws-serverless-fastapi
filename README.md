## Tasks POC

A small FastAPI task API organized with a clean-architecture style:

- `domain`: entities and repository contracts
- `application`: use cases
- `infrastructure`: concrete repository implementations
- `presentation`: HTTP routes and request/response schemas

### Run locally

```powershell
uv sync
uv run uvicorn app.main:app --app-dir src --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

### Endpoints

```powershell
# Health check
Invoke-RestMethod http://127.0.0.1:8000/health

# Create a task
$task = Invoke-RestMethod http://127.0.0.1:8000/tasks -Method Post -ContentType 'application/json' -Body '{"title":"Learn SAM"}'

# List tasks
Invoke-RestMethod http://127.0.0.1:8000/tasks

# Mark a task as complete
Invoke-RestMethod "http://127.0.0.1:8000/tasks/$($task.id)/complete" -Method Patch
```

### Tests

```powershell
uv run pytest
```

### Deploy with CloudFormation

Local development remains FastAPI + Uvicorn; use `/docs` for Swagger. In AWS,
Mangum adapts API Gateway HTTP API events to FastAPI in Lambda.

First create a deployment ZIP. This uses `uv` to download Linux wheels directly,
so Docker and SAM are not needed:

```powershell
.\scripts\package_lambda.ps1
```

Upload `dist/lambda.zip` to an S3 bucket, then create or update the stack:

```powershell
aws s3 cp dist/lambda.zip s3://YOUR_ARTIFACT_BUCKET/tasks/lambda.zip

aws cloudformation deploy `
  --template-file infrastructure/cloudformation.yaml `
  --stack-name tasks-poc `
  --capabilities CAPABILITY_IAM `
  --parameter-overrides ArtifactBucket=YOUR_ARTIFACT_BUCKET ArtifactKey=tasks/lambda.zip
```

Retrieve the API URL:

```powershell
aws cloudformation describe-stacks --stack-name tasks-poc `
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text
```

### Deploy from your machine

With AWS CLI credentials already configured, the scripts below do the same work
as the deployment workflow. They use the current AWS CLI default profile, or
accept `-Profile` if you use a named profile:

```powershell
.\scripts\deploy.ps1 `
  -Region ap-southeast-1 `
  -StackName tasks-poc
```

When `-ArtifactBucket` is omitted, the script creates or reuses
`tasks-poc-artifacts-<ACCOUNT_ID>-<REGION>` automatically. Lambda deployment
ZIPs must first be placed in S3 because a standard `AWS::Lambda::Function`
CloudFormation resource accepts its code from S3 (or ECR for container images),
not from a local path. Pass `-ArtifactBucket YOUR_ARTIFACT_BUCKET` only if you
want to use an existing bucket.

For a named CLI profile:

```powershell
.\scripts\deploy.ps1 `
  -Region ap-southeast-1 `
  -Profile my-aws-profile
```

To delete the application stack locally:

```powershell
.\scripts\destroy.ps1 -Region ap-southeast-1 -StackName tasks-poc
```

The destroy script requires an interactive `DESTROY` confirmation and retains
the artifact bucket and bootstrap stack.

The current in-memory repository is intentionally not persistent between Lambda
invocations. Replace it with DynamoDB before using tasks beyond this POC.

### Deploy with GitHub Actions

The workflow in `.github/workflows/deploy.yml` runs tests for pull requests and
pushes to `main`. Deployments are manual only:

```text
pull request / push -> pytest
manual Run workflow (deploy) -> pytest -> package Linux Lambda ZIP -> S3 -> CloudFormation deploy
```

It uses GitHub OIDC for short-lived AWS credentials. Do not create or store an
AWS access key in GitHub Secrets.

#### One-time AWS bootstrap

From a machine that already has administrator access to the target AWS account,
deploy the OIDC provider, artifact bucket, and GitHub deploy role:

```powershell
aws cloudformation deploy `
  --template-file infrastructure/github-oidc-bootstrap.yaml `
  --stack-name tasks-poc-github-bootstrap `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    GitHubOrganization=YOUR_GITHUB_OWNER `
    GitHubRepository=YOUR_REPOSITORY_NAME `
    GitHubBranch=main `
    ArtifactBucketName=YOUR_GLOBALLY_UNIQUE_ARTIFACT_BUCKET
```

If the AWS account already has an IAM OIDC provider for
`token.actions.githubusercontent.com`, do not deploy a second one; reuse the
existing provider and create the deploy role with the same trust policy.

#### GitHub repository variables

In **Settings > Secrets and variables > Actions > Variables**, add these
non-secret values from the bootstrap stack output:

| Variable | Example |
| --- | --- |
| `AWS_REGION` | `ap-southeast-1` |
| `AWS_ROLE_ARN` | `arn:aws:iam::123456789012:role/repository-github-actions-deploy` |
| `AWS_ARTIFACT_BUCKET` | `your-globally-unique-artifact-bucket` |
| `AWS_STACK_NAME` | `tasks-poc` |

The bootstrap deploy role currently has `AdministratorAccess` purely to keep the
POC setup short. Narrow it to the resources and actions your stack needs before
using it in production.

#### Destroy the application stack

In GitHub, open **Actions > Test and deploy > Run workflow**, choose `destroy`,
and enter exactly `DESTROY` as the confirmation value. For a release, choose
`deploy`; that job also runs tests before creating and deploying the ZIP.

The manual `destroy` job deletes only the application stack identified by
`AWS_STACK_NAME` (Lambda, API Gateway, and its execution role). It deliberately
keeps the bootstrap stack and artifact bucket, including uploaded ZIP files.
