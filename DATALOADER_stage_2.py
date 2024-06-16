# imports 
import os
import subprocess

import pandas as pd

from functions.api_func import download_file


# Directory to save the file
save_directory = "data"

# Perception data file
path_perception = os.path.join(save_directory, "public-perception-data.csv")
if not os.path.exists(path_perception):
    url_perception = "https://data.london.gov.uk/download/public-perception-/d2cbb777-d155-4d0d-965b-49b865fc29df/public-perception-data.csv"
    # Download the file
    path_perception = download_file(url_perception, save_directory)

# PAS data file
path_to_PAS = os.path.join(save_directory, "PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx")
if not os.path.exists(path_to_PAS):
    url_PAS = "https://data.london.gov.uk/download/mopac-surveys/c3db2a0c-70f5-4b73-916b-2b0fcd9decc0/PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx"
    # Download the file
    path_to_PAS = download_file(url_PAS, save_directory)
    path_to_PAS = 'data/PAS_T%26Cdashboard_to%20Q3%2023-24'
    

# take the MPS sheet from the xlsx spreadsheet
if not os.path.exists(f"{save_directory}/PAS_T%26Cdashboard_to%20Q3%2023-24_MPS.csv"):
    path_to_PAS = 'data/PAS_T%26Cdashboard_to%20Q3%2023-24'
    df = pd.read_excel(f'{path_to_PAS}.xlsx', sheet_name='MPS', engine='openpyxl')
    df.to_csv(f"{path_to_PAS}_MPS.csv", index=False)
    df = pd.read_csv(f'{path_to_PAS}_MPS.csv')
    df.to_csv(f'{path_to_PAS}_MPS.csv', index=False)
    
# take the Borough sheet from the xlsx spreadsheet
if not os.path.exists(f'{save_directory}/PAS_T%26Cdashboard_to%20Q3%2023-24_Borough.csv' ):
    path_to_PAS = 'data/PAS_T%26Cdashboard_to%20Q3%2023-24'
    df = pd.read_excel(f'{path_to_PAS}.xlsx', sheet_name='Borough', engine='openpyxl')
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)
    df = pd.read_csv(f'{path_to_PAS}_Borough.csv')
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)

# we run the preprocessor such to have needed csv
if not os.path.exists('data/pas_data_ward_level/pre_final.csv'):
    subprocess.run(["python", 'data_preprocessors/PAS_ward_level_preprocessor.py'])

if not os.path.exists("data/met_data/met_crime_data.pkl"):
    subprocess.run('data_preprocessors/MET_crime_preprocessor.py')

if not os.path.exists('data/pas_data_ward_level/PAS_crime.csv'):
    subprocess.run('data_preprocessors/PAS_crime_preprocessor.py')

