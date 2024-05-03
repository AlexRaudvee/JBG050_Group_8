import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

# config imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from config import path_to_data

# create artifacts where we save the images generated during our work
# os.makedirs('artifacts')

def find_month_year_folder(root_folder: str):
    # Get a list of all items in the root folder
    items = os.listdir(root_folder)
    
    # Filter out only directories that match the pattern of month-year
    month_year_folders = [item for item in items if os.path.isdir(os.path.join(root_folder, item)) and len(item) == 7 and item[4] == '-']
    
    # Return the first matching folder (assuming there's only one)
    if month_year_folders:
        return os.path.join(root_folder, month_year_folders[0])
    else:
        raise FileExistsError(f"Make sure that you specified the right path to the data folder, it should contain folder(s) which starts with YYYY-MM type, your path: {root_folder}")


def read_csv_files(root_folder: str):

    root_folder = find_month_year_folder(root_folder)

    dfs = []  # Dictionary to store DataFrames

    # Iterate through all folders and sub-folders
    for root, dirs, files in os.walk(root_folder):
        # Iterate through all files in current folder
        for file in files:
            # Check if file is a CSV
            if file.endswith(".csv"):
                # Read CSV file into a DataFrame
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                
                # Use file name as column name
                column_name = os.path.splitext(file)[0]
                
                # Store DataFrame in dictionary
                dfs.append(pd.DataFrame({column_name : df.columns}))



    # Concatenate all DataFrames into a single DataFrame
        combined_df = pd.concat(dfs, axis=1)

    return combined_df


data_folder = path_to_data

result_df = read_csv_files(data_folder)

# plot the table
fig, ax = plt.subplots(figsize=(550, 15))
ax.axis('off')
table = ax.table(cellText=result_df.values,
                 colLabels=result_df.columns,
                 loc='center')

table.auto_set_font_size(False)
table.set_fontsize(25)

# Set the position of the table to cover the entire figure area
table.scale(1.3, 4)  # Adjust scale as needed to fit the entire table

# Save the table as an image
plt.savefig('artifacts/columns_in_data.png')

