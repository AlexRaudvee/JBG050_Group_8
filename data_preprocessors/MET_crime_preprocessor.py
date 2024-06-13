# imports 

import os
import sys

import pandas as pd

data_dir = 'data/met_data'

# Check if the directory exists
if not os.path.exists(data_dir):
    print(f"Data directory '{data_dir}' does not exist.")
else:
    all_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('-metropolitan-street.csv'):
                all_files.append(os.path.join(root, file))

    # Check if there are any files to read
    if not all_files:
        print(f"No CSV files found in the directory '{data_dir}'.")
    else:
        df_list = [pd.read_csv(file) for file in all_files]

        # Check if there are any DataFrames to concatenate
        if not df_list:
            print("No dataframes to concatenate.")
        else:
            # Combine all dataframes into one
            df_all_years = pd.concat(df_list, ignore_index=True)

try:
    df_all_years.to_pickle('data/met_data/met_crime_data.pkl')
except:
    print("No Data Were Saved")

print(f"Combined {len(all_files)} files into one DataFrame with {len(df_all_years)}")