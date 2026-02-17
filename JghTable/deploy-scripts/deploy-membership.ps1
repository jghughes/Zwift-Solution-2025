# deploy-membership.ps1
$ErrorActionPreference = "Stop"

$storageAccount = "customerzsun"
$container = "`$web"
$sourceFolder = "../membership"
$targetFolder = "membership"

Write-Host "Deploying membership SPA to Azure Blob Storage..." -ForegroundColor Cyan

# Upload all files
az storage blob upload-batch `
    --account-name $storageAccount `
    --destination "$container/$targetFolder" `
    --source $sourceFolder `
    --pattern '*' `
    --content-cache-control "no-cache" `
    --overwrite `
    --only-show-errors

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "URL: https://$storageAccount.blob.core.windows.net/`$web/$targetFolder/" -ForegroundColor Yellow