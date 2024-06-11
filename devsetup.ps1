# get current working directory

$current_dir = (Get-Location).Path + "\src"
# CURRENT_DIR=`pwd`

$env:PYTHONPATH="$env:PYTHONPATH;$current_dir"
# $env:USER_DB=$current_dir/user_db
# $env:SSL_CERT_FILE = "C:\Users\cosgrma\certs\ca-bundle.crt"
# [System.Environment]::SetEnvironmentVariable('SSL_CERT_FILE','C:\Users\cosgrma\certs\ca-bundle.crt')
$env:PATH="$env:PATH;$current_dir\bin"

# Find all pngs recursively in the current directory and write their relative path and name to a file
# Get-ChildItem -Path . -Filter *.png -Recurse | Select-Object -ExpandProperty FullName | Out-File -FilePath .\icon-index.txt
