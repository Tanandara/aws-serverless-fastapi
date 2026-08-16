param(
    [Parameter(Mandatory)]
    [string]$Region,

    [string]$ArtifactBucket,

    [string]$StackName = "tasks-poc",

    [string]$Profile
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$artifactKey = "tasks/$(Get-Date -Format 'yyyyMMddHHmmss')-$(git rev-parse --short HEAD 2>$null).zip"
$awsArguments = @()

if ($Profile) {
    $awsArguments += "--profile", $Profile
}

Push-Location $projectRoot
try {
    & "$PSScriptRoot\package_lambda.ps1"
    if ($LASTEXITCODE -ne 0) { throw "Lambda package creation failed." }

    $identityJson = & aws @awsArguments sts get-caller-identity --region $Region
    if ($LASTEXITCODE -ne 0) { throw "AWS credential validation failed." }
    $accountId = ($identityJson | ConvertFrom-Json).Account

    if (-not $ArtifactBucket) {
        $ArtifactBucket = "tasks-poc-artifacts-$accountId-$Region"
    }

    & aws @awsArguments s3api head-bucket --bucket $ArtifactBucket --region $Region 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating artifact bucket '$ArtifactBucket'..."
        $createBucketArguments = @("s3api", "create-bucket", "--bucket", $ArtifactBucket, "--region", $Region)
        if ($Region -ne "us-east-1") {
            $createBucketArguments += "--create-bucket-configuration", "LocationConstraint=$Region"
        }
        & aws @awsArguments @createBucketArguments
        if ($LASTEXITCODE -ne 0) { throw "Artifact bucket creation failed." }

        & aws @awsArguments s3api put-public-access-block `
            --bucket $ArtifactBucket `
            --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" `
            --region $Region
        if ($LASTEXITCODE -ne 0) { throw "Artifact bucket security configuration failed." }

        & aws @awsArguments s3api put-bucket-versioning `
            --bucket $ArtifactBucket `
            --versioning-configuration Status=Enabled `
            --region $Region
        if ($LASTEXITCODE -ne 0) { throw "Artifact bucket versioning configuration failed." }
    }

    & aws @awsArguments s3 cp "dist\lambda.zip" "s3://$ArtifactBucket/$artifactKey" --region $Region
    if ($LASTEXITCODE -ne 0) { throw "Artifact upload failed." }

    & aws @awsArguments cloudformation deploy `
        --template-file "infrastructure\cloudformation.yaml" `
        --stack-name $StackName `
        --region $Region `
        --capabilities CAPABILITY_IAM `
        --parameter-overrides "ArtifactBucket=$ArtifactBucket" "ArtifactKey=$artifactKey"
    if ($LASTEXITCODE -ne 0) { throw "CloudFormation deployment failed." }

    & aws @awsArguments cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" `
        --output text

    Write-Host "Artifact bucket: $ArtifactBucket"
}
finally {
    Pop-Location
}
