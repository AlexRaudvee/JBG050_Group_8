# here is going to be preprocessing and loading of the dataframes such that we do not have imports from home.py (debugging)

# TO-DO 
# 1. check out which dataframes can be preprocessed here for optimization
# 2. check out if we can store them in the data folder 
# 3. write the script for preprocessing

# we need geojson file preprocessing for sure
# we need preprocessing of the Trust data 
# we need preprocessing and loading of the data relate to questions
# make sure to structure it in the nice flow, such that we do not run something that we do not need (see if we separate it by files)

# MAY BE CREATE A BACKGROUND JOBS FOLDER WHERE WE LOAD WHAT WE NEED IN A SEPARATE FILE AND THEN IMPORT THIS (reduce the data loading time)

# think about the functions for application, may be store them in another file as well

# imports 
import os 
import sys
import inspect
import subprocess

import pandas as pd 
import geopandas as gpd

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

from config import questions_dict

SAVE_DIR = "data"

PATH_PERCEPTION = os.path.join(SAVE_DIR, "public-perception-data.csv")
PATH_PERCEPTION = PATH_PERCEPTION[:-4]  # Remove ".csv" extension

PATH_TO_PAS = os.path.join(SAVE_DIR, "PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx")
PATH_TO_PAS = PATH_TO_PAS[:-5]  # Remove ".xlsx" extension


def get_caller_script():
    """Helper function to determine the actual caller script name."""
    stack = inspect.stack()
    for frame_info in stack:
        # Skip internal frames
        if frame_info.filename.endswith('.py') and not frame_info.filename.endswith('app_data_preprocessor.py'):
            return frame_info.filename
    return None


def preprocess_neighbourhoods():
    geojson_path = os.path.join(SAVE_DIR, 'neighbourhoods_boundary.geojson')
    neighbourhoods = gpd.read_file(geojson_path)
    
    # Preprocess neighbourhoods data
    neighbourhoods.loc[neighbourhoods['borough'] == 'Westminster', 'borough'] = 'City of Westminster'
    
    return neighbourhoods



def HOMEPAGE_data():
    # additional perception data to be added to df_PAS
    df_perception = pd.read_csv(f'{PATH_PERCEPTION}.csv')

    # now read this files for future use in visualization
    df_PAS_MPS = pd.read_csv(f'{PATH_TO_PAS}_MPS.csv')
    df_PAS_Borough = pd.read_csv(f'data/pas_data_ward_level/pre_final.csv')

    # exclude the questions about the perceived crime and ethnic leaning
    df_PAS_Borough = df_PAS_Borough[~df_PAS_Borough['Measure'].isin(['NNQ135A', 'NPQ135A', 'ReNQ147'])]

    # Preprocess the data fro MPS
    df_PAS_MPS['Date'] = df_PAS_MPS['Date'].apply(lambda x: x[:4])

    # Preprocess the data for Borough
    df_PAS_Borough['Total Proportion'] = df_PAS_Borough['Total Proportion'].astype(float)
    df_PAS_Borough = df_PAS_Borough.loc[:, ~df_PAS_Borough.columns.str.contains('^Unnamed')]
    df_PAS_Borough['Total Proportion'] = df_PAS_Borough['Total Proportion'].round(2)

    # decode the question number in to category: 
    # Map the question names to their short descriptions
    question_descriptions = {key: value[1] for key, value in questions_dict.items()}

    # Rename the 'Measure' column in results_df using the question descriptions
    df_PAS_Borough['Measure'] = df_PAS_Borough['Measure'].map(question_descriptions)

    return df_perception, df_PAS_MPS, df_PAS_Borough, question_descriptions




def CRIMEPAGE_data():
    ### LOAD THE DATA ###

    if not os.path.exists("data/met_data/met_crime_data.pkl"):
        subprocess.run('data_preprocessors/MET_crime_preprocessor.py')

    if not os.path.exists('data/pas_data_ward_level/PAS_crime.csv'):
        subprocess.run('data_preprocessors/PAS_crime_preprocessor.py')

    df_PAS_Crime = pd.read_csv('data/pas_data_ward_level/PAS_crime.csv')
    df_MET_Crime = pd.read_pickle('data/met_data/met_crime_data.pkl', )

    df_PAS_Borough_Trust = pd.read_csv(f'{PATH_TO_PAS}_Borough.csv')
    df_PAS_Borough_Trust = pd.DataFrame(df_PAS_Borough_Trust[df_PAS_Borough_Trust['Measure'] == 'Trust MPS'])

    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Kensington & Chelsea', 'Borough'] = 'Kensington and Chelsea'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Hammersmith & Fulham', 'Borough'] = 'Hammersmith and Fulham'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Barking & Dagenham', 'Borough'] = 'Barking and Dagenham'

    # Apply the conversion function to the Date column
    df_PAS_Borough_Trust['Date'] = df_PAS_Borough_Trust['Date'].apply(lambda date_str: date_str[:7])

    return df_PAS_Crime, df_MET_Crime, df_PAS_Borough_Trust

def RECOMMENDATIONPAGE_data():

    #We define the paths to our CSV files for each year
    csv_files = {
        "20-21": r'data/pas_data_ward_level/PAS_ward_level_FY_20_21.csv',
        "19-20": r'data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv',
        "18-19": r'data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv',
        "17-18": r'data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv',
        "15-17": r'data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv'
    }

    #We define here the borough column name for each year
    borough_column_mapping = {
        "20-21": "Borough",
        "19-20": "C2",
        "18-19": "C2",
        "17-18": "C2",
        "15-17": "C2"
    }

    #We define here the ethnic group column name for each year
    ethnic_group_column_mapping = {
        "20-21": "ReNQ147",
        "19-20": "NQ147r",
        "18-19": "NQ147r",
        "17-18": "NQ147r",
        "15-17": "NQ147r"
    }

    #Define the questions and their corresponding statement and values (for the dashboard also)
    questions = {
        "Q13": {
            "statement": "Q13: To what extent are you worried about crime in this area?",
            "values": ["Very worried", "Fairly worried"]
        },
        "Q15": {
            "statement": "Q15: To what extent are you worried about anti-social behaviour in this area?",
            "values": ["Very worried", "Fairly worried"]
        },
        "Q60": {
            "statement": "Q60: Taking everything into account, how good a job do you think the police IN YOUR AREA are doing?",
            "values": ["Poor", "Very poor"]
        },
        "Q62A": {
            "statement": "Q62A: To what extent do you agree with these statements about the police in your area?\
            By 'your area' I mean within 15 minutes' walk from your home. \
            They can be relied on to be there when you need them",
            "values": ["Tend to disagree", "Strongly disagree"]
        },
        "Q62B": {
            "statement": "Q62B: To what extent do you agree with these statements about the police in your area?\
            By 'your area' I mean within 15 minutes' walk from your home. \
            They would treat you with respect if you had contact with them for any reason.",
            "values": ["Tend to disagree", "Strongly disagree"]
        },
        "Q62C": {
            "statement": "Q62C: To what extent do you agree with these statements about the police in your area?\
            By 'your area' I mean within 15 minutes' walk from your home. \
            The police in your area treat everyone fairly regardless of who they are.",
            "values": ["Tend to disagree", "Strongly disagree"]
        },
        "Q62D": {
            "statement": "Q62D: To what extent do you agree with these statements about the police in this area?\
            By 'this area' I mean within 15 minutes' walk from here. They can be relied on to deal with minor crimes",
            "values": ["Tend to disagree", "Strongly disagree"]
        },
        "Q62E": {
            "statement": "Q62E: To what extent do you agree with these statements about the police in this area?\
            By 'this area' I mean within 15 minutes' walk from here. They understand the issues that affect this community",
            "values": ["Tend to disagree", "Strongly disagree"]
        },
        "Q62TG": {
            "statement": "Q62TG: To what extent do you agree with these statements about the police in your area? \
            By 'your area' I mean within 15 minutes' walk from your home. \
            The police in your area listen to the concerns of local people.",
            "values": ["Tend to disagree","Strongly disagree"]
        },
        "A121": {
            "statement": "A121: How confident are you that the Police in your area use their stop and search powers fairly?",
            "values": ["Not very confident", "Not at all confident"]
        }, 
        "Q62F": {
            "statement": "Q62F: To what extent do you agree with these statements about the police in your area?\
            By 'your area' I mean within 15 minutes' walk from your home.\
            They are dealing with the things that matter to people in this community",
            "values": ["Tend to disagree","Strongly disagree"]
        },
        "Q62H": {
            "statement": "Q62H: To what extent do you agree with these statements about the police in this area?\
            By 'this area' I mean within 15 minutes' walk from here. The police in this area are helpful",
            "values": ["Tend to disagree","Strongly disagree"]
        },
        "Q62TI": {
            "statement": "Q62TI: To what extent do you agree with these statements about the police in this area?\
            By 'this area' I mean within 15 minutes' walk from here. The police in this area are friendly and approachable",
            "values": ["Tend to disagree","Strongly disagree"]
        },
        "Q62TJ": {
            "statement": "Q62TJ: To what extent do you agree with these statements about the police in this area?\
            By 'this area' I mean within 15 minutes' walk from here. The police in this area are easy to contact",
            "values": ["Tend to disagree", "strongly disagree"]
        },
        "NQ135BD": {
            "statement": "NQ135BD: To what extent do you agree or disagree with the following statements:\
            The Metropolitan Police Service is an organisation that I can trust",
            "values": ["Tend to disagree", "strongly disagree"]
        },
        "NQ135BH": {
            "statement": "NQ135BH: To what extent do you agree or disagree that\
            the police in your local area are sufficiently held accountable for their actions?",
            "values": ["Tend to disagree", "strongly disagree"]
        }
    }

    df_PAS_Borough_Trust = pd.read_csv(f'{PATH_TO_PAS}_Borough.csv')
    df_PAS_Borough_Trust = pd.DataFrame(df_PAS_Borough_Trust[df_PAS_Borough_Trust['Measure'] == 'Trust MPS'])

    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Kensington & Chelsea', 'Borough'] = 'Kensington and Chelsea'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Hammersmith & Fulham', 'Borough'] = 'Hammersmith and Fulham'
    df_PAS_Borough_Trust.loc[df_PAS_Borough_Trust['Borough'] == 'Barking & Dagenham', 'Borough'] = 'Barking and Dagenham'

    # Apply the conversion function to the Date column
    df_PAS_Borough_Trust['Date'] = df_PAS_Borough_Trust['Date'].apply(lambda date_str: date_str[:7])

    return csv_files, borough_column_mapping, ethnic_group_column_mapping, questions, df_PAS_Borough_Trust