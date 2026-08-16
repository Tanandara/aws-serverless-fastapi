param(
    [Parameter(Mandatory)]
    [string]$Region,

    [string]$StackName = "tasks-poc",

    [string]$Profile
)

$ErrorActionPreference = "Stop"
$confirmation = Read-Host "This deletes the application stack '$StackName'. Type DESTROY to continue"

if ($confirmation -cne "DESTROY") {
    Write-Host "Cancelled."
    exit 0
}

$awsArguments = @()
if ($Profile) {
    $awsArguments += "--profile", $Profile
}

& aws @awsArguments sts get-caller-identity --region $Region
if ($LASTEXITCODE -ne 0) { throw "AWS credential validation failed." }

& aws @awsArguments cloudformation delete-stack --stack-name $StackName --region $Region
if ($LASTEXITCODE -ne 0) { throw "CloudFormation delete request failed." }

& aws @awsArguments cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
if ($LASTEXITCODE -ne 0) { throw "CloudFormation stack deletion failed." }

Write-Host "Deleted application stack '$StackName'. The artifact bucket and bootstrap stack were not changed."
