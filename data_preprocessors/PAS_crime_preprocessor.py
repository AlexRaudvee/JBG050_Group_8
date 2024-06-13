# imports 
import os
import sys

import pandas as pd
from datetime import datetime

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 



# TO-DO
# 1. Construct the dataframe which is going to be used for crime comparison so:
# We need the following columns in the dataframe: Date, Borough, Crime type that people see as a frequent crime


# Define the path to the CSV file
csv_file_paths = [r'data/PAS_data_ward_level/PAS_ward_level_FY_20_21.csv', r'data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv', r'data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv', r'data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv', r'data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv']

results_dfs = []
for csv_file_path in csv_file_paths:
    # Define the column name for borough
    borough_column = 'Borough' if csv_file_path[-9:-4] == '20_21' else 'C2'
    column_name = 'NPQ135A' if (csv_file_path[-9:-4] == '20_21') or (csv_file_path[-9:-4] == '19_20') else 'PQ135AA'

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Function to extract the month and year
    def convert_date_format(date_str):
        # Split the string by parentheses and extract the part containing the month and year
        month_year_str = date_str.split('(')[1].split(')')[0]
        # Parse the month and year and format it as 'YYYY-MM'
        return datetime.strptime(month_year_str, '%b %Y').strftime('%Y-%m')

    # Apply the function to the MONTH column
    df['MONTH'] = df['MONTH'].apply(convert_date_format)

    # Group the DataFrame by the "Borough" column
    grouped_df = df.groupby([borough_column, "MONTH"])[column_name]

        
    # Create a new DataFrame to store the results
    results_df = pd.DataFrame(columns=['Date', 'Borough', 'Crime type'])

    # Iterate over each question and borough to calculate proportions

    for (borough, month), group_df in grouped_df:

        metric_stats = group_df.value_counts().to_dict()

        results_df = results_df.append({'Date': month,
                                        'Borough': borough,
                                        'Crime type': metric_stats}, ignore_index=True)    
    
    results_dfs.append(results_df)


# concat the dataframes
results_df = pd.concat(results_dfs, ignore_index=True)

results_df.loc[results_df['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'
results_df.loc[results_df['Borough'] == 'Kensington & Chelsea', 'Borough'] = 'Kensington and Chelsea'
results_df.loc[results_df['Borough'] == 'Hammersmith & Fulham', 'Borough'] = 'Hammersmith and Fulham'
results_df.loc[results_df['Borough'] == 'Barking & Dagenham', 'Borough'] = 'Barking and Dagenham'
results_df.loc[results_df['Borough'] == 'Westminster', 'Borough' ] = 'City of Westminster'  

# save the resulting DataFrame
results_df.to_csv('data/pas_data_ward_level/PAS_crime.csv')


