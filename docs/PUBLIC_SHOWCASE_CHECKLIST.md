# Public showcase checklist

Use this checklist before publishing the repository or leaving the AWS POC
deployed.

## Repository

- Do not commit `.env` files, AWS access keys, session tokens, SSO start URLs,
  account IDs, role ARNs, real bucket names, private keys, or local DynamoDB
  data.
- The `AWS_ACCESS_KEY_ID=local` and `AWS_SECRET_ACCESS_KEY=local` examples are
  dummy values for DynamoDB Local only; they are not AWS credentials.
- Review staged changes before each push:

  ```powershell
  git add -A
  git diff --cached
  ```

## AWS POC account

- The API is deliberately public so `/docs` can be demonstrated. Do not put
  sensitive data in it. The template limits API Gateway to 5 steady requests
  per second with a burst of 10; throttling limits abuse but is not
  authentication.
- Use a CloudFormation change set for every infrastructure update.
- Delete the `tasks-poc` stack when the showcase is not needed. The current
  DynamoDB table is deleted with the stack.

## Artifact bucket created manually in the console

The bootstrap template configures lifecycle rules automatically, but a bucket
created manually is not governed by that template. In the S3 Console, add a
lifecycle rule that:

1. Applies to all objects (or the `tasks/` prefix if you use it).
2. Expires **noncurrent versions** after 30 days.
3. Aborts incomplete multipart uploads after 7 days.

Do not expire the current Lambda ZIP version while the stack still references
it. S3 Versioning is useful for rollback; this rule only cleans older versions.

## GitHub Actions

- Keep `AWS_REGION`, `AWS_ROLE_ARN`, `AWS_ARTIFACT_BUCKET`, and
  `AWS_STACK_NAME` as GitHub repository variables, not source code.
- Use GitHub OIDC; do not add long-lived AWS access keys to GitHub Secrets.
- The OIDC deploy policy is intentionally limited to the AWS services used by
  this POC. For production, use a permissions boundary or CloudFormation
  service role with resource names restricted to your deployment environment.
