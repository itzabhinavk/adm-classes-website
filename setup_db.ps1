# Setup the ADM MySQL database and import the schema
# Usage: Run this script from the ADM project folder in PowerShell.

$mysqlCmd = Get-Command mysql.exe -ErrorAction SilentlyContinue
if (-not $mysqlCmd) {
    Write-Error 'mysql.exe not found in PATH. Please install MySQL or add it to PATH.'
    exit 1
}

$dbUser = 'root'
$dbName = 'adm'
$sqlPath = Join-Path $PSScriptRoot 'database\users.sql'

if (-not (Test-Path $sqlPath)) {
    Write-Error "SQL file not found: $sqlPath"
    exit 1
}

$password = Read-Host -AsSecureString "Enter MySQL password for $dbUser (leave blank if none)"
if ($password.Length -eq 0) {
    $pwdArg = ''
} else {
    $pwdPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    $pwdArg = "--password=$pwdPlain"
}

Write-Host "Creating database '$dbName'..."
& $mysqlCmd.Source -u $dbUser $pwdArg -e "CREATE DATABASE IF NOT EXISTS $dbName;" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Failed to create database. Check MySQL credentials and try again.'
    exit 1
}

Write-Host "Importing schema from '$sqlPath' into database '$dbName'..."
Get-Content -Raw -Path $sqlPath | & $mysqlCmd.Source -u $dbUser $pwdArg $dbName
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Failed to import SQL schema. Verify the SQL file and MySQL credentials.'
    exit 1
}

Write-Host "Database setup completed successfully."
