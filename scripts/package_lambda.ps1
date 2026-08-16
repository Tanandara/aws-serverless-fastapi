param(
    [string]$OutputDirectory = "dist"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $projectRoot $OutputDirectory
$packagePath = Join-Path $outputPath "lambda.zip"
$stagingPath = Join-Path $outputPath "lambda-package"

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $stagingPath
Remove-Item -Force -ErrorAction SilentlyContinue $packagePath
New-Item -ItemType Directory -Force $stagingPath | Out-Null

Push-Location $projectRoot
try {
    uv export --no-dev --no-emit-project --format requirements-txt --output-file "$stagingPath\requirements.txt"
    uv pip install --target $stagingPath --requirement "$stagingPath\requirements.txt" --python-version 3.14 --python-platform linux --only-binary :all:
    Remove-Item "$stagingPath\requirements.txt"
    Copy-Item -Recurse -Force "$projectRoot\src\app" $stagingPath
    Compress-Archive -Path "$stagingPath\*" -DestinationPath $packagePath -Force
}
finally {
    Pop-Location
}

Write-Host "Created $packagePath"
