# FastAPI + Lambda + DynamoDB POC runbook

This runbook records the decisions and manual workflow for this POC.

## What is deployed

```text
API Gateway HTTP API -> AWS Lambda -> Mangum -> FastAPI
                                      |
                                      +-> DynamoDB Tasks table
```

`app.main.handler` is the Lambda handler. Mangum converts API Gateway HTTP API
payload v2 events into ASGI requests. FastAPI serves `/docs` and `/openapi.json`
through the same public API URL.

## Repository selection

| Environment | Repository | Required configuration |
| --- | --- | --- |
| Local default | `InMemoryTaskRepository` | None |
| Local DynamoDB | `DynamoDBTaskRepository` | `TASKS_TABLE_NAME`, `DYNAMODB_ENDPOINT_URL` |
| AWS Lambda | `DynamoDBTaskRepository` | `TASKS_TABLE_NAME` supplied by CloudFormation |

The domain repository contract is unchanged between implementations.

## Local workflows

### FastAPI only

```powershell
uv sync
uv run uvicorn app.main:app --app-dir src --reload
```

Swagger UI: `http://127.0.0.1:8000/docs`

### DynamoDB Local (optional)

This is not required for unit tests.

```powershell
docker compose up -d dynamodb
.\scripts\create_local_dynamodb_table.ps1

$env:TASKS_TABLE_NAME = "tasks-local"
$env:DYNAMODB_ENDPOINT_URL = "http://localhost:8001"
$env:AWS_ACCESS_KEY_ID = "local"
$env:AWS_SECRET_ACCESS_KEY = "local"
$env:AWS_DEFAULT_REGION = "ap-southeast-1"

uv run uvicorn app.main:app --app-dir src --reload
```

Stop it with `docker compose down`. Its data is persisted under
`docker/dynamodb/`, which is ignored by Git.

## Manual AWS deployment

Use AWS IAM Identity Center / SSO with a named AWS CLI profile. Verify the
target account before each deployment:

```powershell
aws sso login --profile YOUR_PROFILE
aws sts get-caller-identity --profile YOUR_PROFILE
```

### First deployment

1. Package the Linux Lambda ZIP:

   ```powershell
   .\scripts\package_lambda.ps1
   ```

2. Upload `dist/lambda.zip` to an S3 artifact bucket.
3. In CloudFormation Console, create a stack from
   `infrastructure/cloudformation.yaml`.
4. Set `ArtifactBucket` and `ArtifactKey` to the uploaded object.
5. Acknowledge IAM resource creation, then create the stack.
6. Read the `ApiUrl` stack output. Swagger is `<ApiUrl>/docs`.

### Update an existing stack using S3 Versioning

1. Package the ZIP again.
2. Upload it over the same S3 key.
3. Copy the new object's **Version ID** from S3.
4. In CloudFormation Console, choose **Update stack > Create a change set**.
5. Upload the current CloudFormation template.
6. Set `ArtifactBucket`, `ArtifactKey`, and `ArtifactVersion`.
7. Review the change set before executing it.

CloudFormation only sees changes to its declared properties. Reusing the same
bucket and key does not by itself signal new Lambda code; `ArtifactVersion`
maps to Lambda `S3ObjectVersion` and makes the update explicit.

## CloudFormation resources

- `TasksTable`: on-demand DynamoDB table with string partition key `id`.
- `TasksFunctionRole`: Lambda log permissions plus only `GetItem`, `PutItem`,
  and `Scan` against `TasksTable`.
- `TasksFunction`: Python 3.14 Lambda receiving `TASKS_TABLE_NAME`.
- `HttpApi`, `LambdaIntegration`, `RootRoute`, `ProxyRoute`, and `ApiStage`:
  public API Gateway HTTP API with Lambda proxy integration.

The table currently has no explicit `DeletionPolicy`, so deleting the stack
deletes the table and its data. Decide explicitly whether to use
`DeletionPolicy: Retain` before treating this as a non-POC environment.

## CI/CD status

`.github/workflows/deploy.yml` is configured for:

```text
Pull request / push to main -> test only
Manual workflow (deploy) -> test -> build ZIP -> S3 -> CloudFormation
Manual workflow (destroy) -> requires DESTROY -> delete application stack
```

It uses GitHub OIDC and repository variables. The one-time OIDC/bootstrap
template is `infrastructure/github-oidc-bootstrap.yaml`.

## Next sensible improvements

1. Add DynamoDB Local integration tests for the HTTP task lifecycle.
2. Decide data-retention and backup policy for the DynamoDB table.
3. Replace `Scan` with a query/index strategy if task listing needs filtering or
   user ownership.
4. Add authentication before exposing tasks beyond this learning POC.
