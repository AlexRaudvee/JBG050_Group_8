# imports 
import os
import sys

import pandas as pd
from datetime import datetime

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# config imports 
from config import questions_dict, weighted_questions, weights



### FUNCTIONS ###

# Function to extract the month and year
def convert_date_format(date_str):
    # Split the string by parentheses and extract the part containing the month and year
    month_year_str = date_str.split('(')[1].split(')')[0]
    # Parse the month and year and format it as 'YYYY-MM'
    return datetime.strptime(month_year_str, '%b %Y').strftime('%Y-%m')



### LOADING AND PREPROCESSING ###

# Define the path to the CSV file
csv_file_path = r'data/PAS_data_ward_level/PAS_ward_level_FY_20_21.csv'

# Define the column name for borough
borough_column = 'Borough' if csv_file_path[-9:-4] == '20_21' else 'BOROUGHNEIGHBOURHOODCODED'

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Apply the function to the MONTH column
df['MONTH'] = df['MONTH'].apply(convert_date_format)

# Group the DataFrame by the "Borough" column
grouped_df = df.groupby([borough_column, "MONTH"])

    
# Create a new DataFrame to store the results
results_df = pd.DataFrame(columns=['Date', 'Borough', 'Measure', 'Total Proportion', 'White_British_Proportion', 'White_Other_Proportion', 'Black_Proportion', 'Asian_Proportion', 'Mixed_Proportion', 'Other_Proportion'])

# Iterate over each question and borough to calculate proportions
for question in questions_dict.keys():
    for (borough, month), group_df in grouped_df:
        date = month
        measure = question
        borough = borough

        try:
            # Calculate the total proportion
            if question not in weighted_questions:
                value_counts = group_df[question].value_counts()
                summ = value_counts.sum()

                for ans in value_counts.keys():
                    try:
                        value_counts[ans] = value_counts[ans] * weights.get(ans)        
                    except:
                        print(value_counts)
                        break
                total_proportion = value_counts.sum()/ summ
            else:
                continue

            # Extract the ethnic group proportions
            white_british_proportion = group_df[group_df['ReNQ147'] == 'White British'].shape[0] / group_df.shape[0]
            black_proportion = group_df[group_df['ReNQ147'] == 'Black'].shape[0] / group_df.shape[0]
            asian_proportion = group_df[group_df['ReNQ147'] == 'Asian'].shape[0] / group_df.shape[0]
            white_other_proportion = group_df[group_df['ReNQ147'] == 'White Other'].shape[0] / group_df.shape[0]
            mixed_proportion = group_df[group_df['ReNQ147'] == 'Mixed'].shape[0] / group_df.shape[0]
            other_ethnicity_proportion = 1 - white_british_proportion - white_other_proportion - black_proportion - asian_proportion  # Assuming there are only 'White' and 'Black' ethnicities
            
            # Append the results to the DataFrame
            results_df = results_df.append({
                'Date': date,
                'Borough': borough,
                'Measure': measure,
                'Total Proportion': total_proportion,
                'White_British_Proportion': white_british_proportion,
                'White_Other_Proportion': white_other_proportion,
                'Black_Proportion': black_proportion,
                'Asian_Proportion': asian_proportion,
                'Mixed_Proportion': mixed_proportion,
                'Other_Proportion': other_ethnicity_proportion
            }, ignore_index=True)
        except KeyError as e:
            print(f"given question ({question}) didn't occur in {csv_file_path[-9:-4]}")
         
 
# renaming values
results_df.loc[results_df['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'
results_df.loc[results_df['Borough'] == 'Kensington & Chelsea', 'Borough'] = 'Kensington and Chelsea'
results_df.loc[results_df['Borough'] == 'Hammersmith & Fulham', 'Borough'] = 'Hammersmith and Fulham'
results_df.loc[results_df['Borough'] == 'Barking & Dagenham', 'Borough'] = 'Barking and Dagenham'
results_df.loc[results_df['Borough'] == 'Westminster', 'Borough' ] = 'City of Westminster'

# Print the resulting DataFrame
results_df.to_csv('data/pas_data_ward_level/pre_final.csv')
