# Powershell Script to unzip all zip files into a directory name by removing "2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee" in the filename
# and then unzipping the files into the directory
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2023-10-26-18-26-53.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2023-11-05-20-59-55.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2024-01-27-19-15-34.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2024-04-19-00-08-58.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2024-04-27-20-42-15.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2024-05-10-02-10-36.zip
# 2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee-2024-05-24-03-30-50.zip

$chatgpt_uid = "2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee"
# Get all zip files in the current directory
$zipFiles = Get-ChildItem -Path . -Filter "*.zip"

# Loop through all zip files
foreach ($zipFile in $zipFiles) {
    # Get the new directory name by removing "2f0b24391e2337e996d72d9c5b02b4a5c88e14f9d89fb90a7579522b28e87aee" from the filename
    $directoryName = $zipFile.Name -replace "$chatgpt_uid-", ""

    # Create the new directory
    New-Item -ItemType Directory -Path $directoryName -Force

    # Unzip the file into the new directory
    Expand-Archive -Path $zipFile.FullName -DestinationPath $directoryName
}
