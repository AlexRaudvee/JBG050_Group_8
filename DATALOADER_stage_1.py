import io
import os
import sys
import zipfile
import requests
import subprocess

from tqdm import tqdm
from config import LAST_AVAILABLE_DATASET

def ask_user_input():
    # Detect the platform and open a new terminal to ask for input
    if sys.platform.startswith('win'):
        subprocess.run('start cmd /k python -c "input(\'Do you want to run the dataloader? (Y/Yes to proceed): \')"', shell=True)
    elif sys.platform.startswith('darwin'):  # macOS
        subprocess.run(['osascript', '-e', 'tell application "Terminal" to do script "python -c \'input(\\\"Do you want to run the dataloader? (Y/Yes to proceed): \\\")\'"'])
    elif sys.platform.startswith('linux'):
        subprocess.run(['gnome-terminal', '--', 'python3', '-c', 'input("Do you want to run the dataloader? (Y/Yes to proceed): ")'])
    else:
        print("Unsupported operating system.")
        return None

    return input("Do you want to run the dataloader? (Y/Yes to proceed): ")


# Ask the user for input
print("For loading the dataset, you need to have 5-6 Gb of memory available for this datasets\n")
user_input = ask_user_input()

# Check if the input is 'Y' or 'Yes'
if user_input.lower() in ['y', 'yes']:

    print("Good, here we go... \n")

    urls = [
        'https://data.police.uk/data/archive/2016-12.zip',
        'https://data.police.uk/data/archive/2019-12.zip',
        'https://data.police.uk/data/archive/2022-12.zip',
        'https://data.police.uk/data/archive/2024-03.zip'
    ]
 
    if LAST_AVAILABLE_DATASET is not None:
        urls.append(LAST_AVAILABLE_DATASET)

    # Define the target directory for extraction
    target_dir = 'data/met_data'

    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    custom_format = "{desc}: {percentage:.0f}%\x1b[33m|\x1b[0m\x1b[32m{bar}\x1b[0m\x1b[31m{remaining}\x1b[0m\x1b[33m|\x1b[0m {n}/{total} [{elapsed}<{remaining}]"

    epoch = 1
    for url in urls:
        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            # Create a BytesIO object from the response content
            zip_file = io.BytesIO(response.content)

            # Open the zip file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # List all files in the zip archive
                all_files = zip_ref.namelist()

                # Filter files of interest
                target_files = [f for f in all_files if 'metropolitan' in f]

                # Extract only the target files to the target directory
                for file in tqdm(target_files, desc=f"Downloading files epoch {epoch}/{len(urls)}", dynamic_ncols=True, bar_format=custom_format, ascii=' -'):
                    zip_ref.extract(file, target_dir)
                
                print(f'Files extracted and saved to {target_dir}\n')
            epoch += 1
        else:
            print(f"Failed to download file. Status code: {response.status_code}, {response.url} may not be valid, make sure that link in form of {urls[0]}\n")

    # Verify extraction by listing the extracted files (Optional)
    extracted_files = os.listdir(target_dir)
    print("Extracted files:", extracted_files, '\n')

else:
    print("Dataloader was not run. Exiting shuting down.")
