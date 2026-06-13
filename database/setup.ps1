# Deploy IMS schema, triggers, procedures, and seed data to local MySQL.
param(
    [string]$Host = "localhost",
    [int]$Port = 3306,
    [string]$User = "root",
    [string]$Password = ""
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Invoke-MySqlFile {
    param([string]$FilePath)
    Write-Host "Running $FilePath ..."
    if ($Password) {
        Get-Content $FilePath -Raw | mysql -h $Host -P $Port -u $User -p$Password
    } else {
        Get-Content $FilePath -Raw | mysql -h $Host -P $Port -u $User
    }
}

$files = @(
    "01_schema.sql",
    "02_triggers_and_views.sql",
    "03_stored_procedures.sql",
    "04_seed_data.sql"
)

foreach ($file in $files) {
    Invoke-MySqlFile (Join-Path $scriptDir $file)
}

Write-Host "IMS database deployed successfully."
