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
from config import questions_dict

# Define the weights for each category
weights = {
    'Strongly disagree': 0,
    'Disagree': 0.25,
    'Neither agree nor disagree': 0.5,
    'Agree': 0.75,
    'Strongly agree': 1,
    'Not at all worried': 0.1,
    'Not very worried': 0.3,
    'Fairly worried': 0.6,
    'Very worried': 0.9,
    'Poor': 0.2,
    'Fair': 0.4,
    'Good': 0.6,
    'Excellent': 0.8,
    'Very poor': 0.1,
    'Tend to agree': 0.6,
    'Strongly agree': 1,
    'Neither agree nor disagree': 0.5,
    'Tend to disagree': 0.4,
    'Fairly confident': 0.6,
    'Very confident': 0.8,
    'Not very confident': 0.3,
    'Not at all confident': 0.1,
    'Major problem': 0.8,
    'Minor problem': 0.5,
    'Not a problem at all': 0.2
}

weighted_questions = {'NNQ135A', 'NPQ135A', 'ReNQ147'}

# Define the path to the CSV file
csv_file_path = r'data/PAS_data_ward_level/PAS_ward_level_FY_20_21.csv'

# Define the column name for borough
borough_column = 'Borough' if csv_file_path[-9:-4] == '20_21' else 'BOROUGHNEIGHBOURHOODCODED'

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
            if question in weighted_questions:
                value_counts = group_df[question].value_counts(normalize=True)
                total_proportion = sum(value_counts[category] * weights.get(category, 0) for category in value_counts.index)
            else:
                value_counts = group_df[question].value_counts(normalize=True)
                total_proportion = sum(value_counts[category] * weights.get(category, 0) for category in value_counts.index)
            
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

# Print the resulting DataFrame
results_df.to_csv('data/pas_data_ward_level/pre_final.csv')
