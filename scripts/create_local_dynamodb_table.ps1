param(
    [string]$TableName = "tasks-local",
    [string]$EndpointUrl = "http://localhost:8001",
    [string]$Region = "ap-southeast-1"
)

$ErrorActionPreference = "Stop"

& aws dynamodb describe-table `
    --table-name $TableName `
    --endpoint-url $EndpointUrl `
    --region $Region 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "DynamoDB Local table '$TableName' already exists."
    exit 0
}

& aws dynamodb create-table `
    --table-name $TableName `
    --attribute-definitions AttributeName=id,AttributeType=S `
    --key-schema AttributeName=id,KeyType=HASH `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url $EndpointUrl `
    --region $Region

if ($LASTEXITCODE -ne 0) { throw "DynamoDB Local table creation failed." }

Write-Host "Created DynamoDB Local table '$TableName'."
