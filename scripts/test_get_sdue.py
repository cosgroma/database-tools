import os
from pathlib import Path

# Specify the network share path
network_share_path = r"\\oursites.myngc.com@SSL\DavWWWRoot\MS\EML01\WHEng\01Lib\14AC_T\PROPOSALS\SDUE"

# Get the list of files in the network share
file_list = os.listdir(network_share_path)

# Print the list of files
for file_name in file_list:
    print(file_name)

# recusrive search for files in the network share
for root, _, files in os.walk(network_share_path):
    for file in files:
        print(Path(root) / file)

# Get list of top level directories
top_level_dirs = [d for d in os.listdir(network_share_path) if Path(network_share_path) / d.is_dir()]


for d in top_level_dirs:
    print(d)
