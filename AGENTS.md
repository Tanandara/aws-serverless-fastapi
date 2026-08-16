# Project instructions

This repository is a learning POC for FastAPI on AWS Lambda behind API Gateway
HTTP API. Read `docs/POC_RUNBOOK.md` before changing deployment or persistence.

## Architecture

- Keep domain and application layers independent of FastAPI, AWS, and DynamoDB.
- Routes only translate HTTP input/output and invoke use cases.
- Repository implementations belong in `src/app/infrastructure/repositories/`.
- `InMemoryTaskRepository` is the default for local FastAPI development.
- `DynamoDBTaskRepository` is selected only when `TASKS_TABLE_NAME` is set.

## Local development

- Default FastAPI/Swagger: `uv run uvicorn app.main:app --app-dir src --reload`
- Unit tests must not require Docker, AWS credentials, or a running DynamoDB.
- DynamoDB Local is optional and runs via `docker compose up -d dynamodb`.
- When using DynamoDB Local, set `TASKS_TABLE_NAME`,
  `DYNAMODB_ENDPOINT_URL`, and dummy AWS credential environment variables as
  documented in the runbook.

## AWS deployment

- Deployment is raw CloudFormation, not AWS SAM. Do not reintroduce SAM unless
  explicitly requested.
- Lambda is packaged as a Linux ZIP with `scripts/package_lambda.ps1` and
  uploaded to an S3 artifact bucket before a CloudFormation update.
- The CloudFormation template is `infrastructure/cloudformation.yaml`.
- When reusing an S3 object key, pass its new S3 Version ID as
  `ArtifactVersion`; otherwise CloudFormation may not update Lambda code.
- Use a CloudFormation change set for infrastructure changes and review all
  additions, modifications, replacements, and deletions before execution.
- Do not store AWS account IDs, access keys, SSO URLs, bucket names, or role
  ARNs in committed files. Use parameters, environment variables, or GitHub
  repository variables.

## Verification

- Run `uv run pytest` after code changes.
- Validate PowerShell scripts with the PowerShell parser when they change.
- Validate YAML syntax after CloudFormation or GitHub workflow changes.
