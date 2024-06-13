# imports 
import os
import sys
import folium
import subprocess

import pandas as pd
import streamlit as st
import geopandas as gpd
import branca.colormap as cm

from streamlit_folium import st_folium

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# custom imports
from config import questions_dict
from functions.api_func import download_file
from app.app_data_preprocessor import preprocess_neighbourhoods

# LOAD THE DATA

neighbourhoods = preprocess_neighbourhoods()

# we run the preprocessor such to have needed csv
if not os.path.exists('data/pas_data_ward_level/pre_final.csv'):
    subprocess.run(["python", 'data_preprocessors/PAS_prerocess_ward_level.py'])

# Directory to save the file
save_directory = "data"

# Perception data file
path_perception = os.path.join(save_directory, "public-perception-data.csv")
if not os.path.exists(path_perception):
    url_perception = "https://data.london.gov.uk/download/public-perception-/d2cbb777-d155-4d0d-965b-49b865fc29df/public-perception-data.csv"
    # Download the file
    path_perception = download_file(url_perception, save_directory)

path_perception = path_perception[:-4]  # Remove ".csv" extension

# PAS data file
path_to_PAS = os.path.join(save_directory, "PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx")
if not os.path.exists(path_to_PAS):
    url_PAS = "https://data.london.gov.uk/download/mopac-surveys/c3db2a0c-70f5-4b73-916b-2b0fcd9decc0/PAS_T%26Cdashboard_to%20Q3%2023-24.xlsx"
    # Download the file
    path_to_PAS = download_file(url_PAS, save_directory)

path_to_PAS = path_to_PAS[:-5]  # Remove ".xlsx" extension

# take the MPS sheet from the xlsx spreadsheet
if not os.path.exists(f"{save_directory}/PAS_T%26Cdashboard_to%20Q3%2023-24_MPS.csv"):
    df = pd.read_excel(f'{path_to_PAS}.xlsx', sheet_name='MPS', header=0)
    df.to_csv(f"{path_to_PAS}_MPS.csv", index=False)
    df = pd.read_csv(f'{path_to_PAS}_MPS.csv')
    df.to_csv(f'{path_to_PAS}_MPS.csv', index=False)
    
# take the Borough sheet from the xlsx spreadsheet
if not os.path.exists(f'{save_directory}/PAS_T%26Cdashboard_to%20Q3%2023-24_Borough.csv' ):
    df = pd.read_excel(f'{path_to_PAS}.xlsx', sheet_name='Borough', header=0)
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)
    df = pd.read_csv(f'{path_to_PAS}_Borough.csv')
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)

# additional perception data to be added to df_PAS
df_perception = pd.read_csv(f'{path_perception}.csv')

# now read this files for future use in visualization
df_PAS_MPS = pd.read_csv(f'{path_to_PAS}_MPS.csv')
df_PAS_Borough = pd.read_csv(f'data/pas_data_ward_level/pre_final.csv')

# exclude the questions about the perceived crime and ethnic leaning
df_PAS_Borough = df_PAS_Borough[~df_PAS_Borough['Measure'].isin(['NNQ135A', 'NPQ135A', 'ReNQ147'])]

# Preprocess the data fro MPS
df_PAS_MPS['Date'] = df_PAS_MPS['Date'].apply(lambda x: x[:4])

# Preprocess the data for Borough
df_PAS_Borough['Total Proportion'] = df_PAS_Borough['Total Proportion'].astype(float)
df_PAS_Borough = df_PAS_Borough.loc[:, ~df_PAS_Borough.columns.str.contains('^Unnamed')]
df_PAS_Borough['Borough'] = df_PAS_Borough['Borough'].apply(lambda x: 'Westminster' if x == 'City of Westminster' else x)
df_PAS_Borough['Total Proportion'] = df_PAS_Borough['Total Proportion'].round(2)

# decode the question number in to category: 
# Map the question names to their short descriptions
question_descriptions = {key: value[1] for key, value in questions_dict.items()}

# Rename the 'Measure' column in results_df using the question descriptions
df_PAS_Borough['Measure'] = df_PAS_Borough['Measure'].map(question_descriptions)


# DEFINE THE FUNCTIONS 
    
def display_map(df: pd.DataFrame, date: str, measure: str, map_key: str):
        
    # Filter data based on selected date
    filtered_data = df[(df['Measure'] == measure) & (df['Date'] == date)]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods.merge(filtered_data, left_on='borough', right_on='Borough'))

    # create the color map 
    linear = cm.LinearColormap(["red", "yellow", "green"], vmin=min(merged_data['Total Proportion']), vmax=max(merged_data['Total Proportion']))

    # create the map
    m = folium.Map(location=[51.5074, -0.1278], tiles="Cartodb Positron", zoom_start=10.5)

    # geojson layer for the map
    geojson_layer = folium.features.GeoJson(
            data=merged_data,
            style_function=lambda feature: {
                "fillColor": linear(feature['properties']['Total Proportion']),
                "color": "black",
                "weight": 1,
                "dashArray": "5, 5",
            },
            tooltip=folium.features.GeoJsonTooltip(fields=['borough', 'name', 'Total Proportion'],
                                                   aliases=['Borough', 'Location', 'Proportion']))
    # add layer to the map
    geojson_layer.add_to(m)

    # define the callback 

    return st_folium(m, width=1000, height=1000, key=map_key)

def comparison_page():
    """
    This function sets up the Streamlit dashboard for comparison mode.
    """
    st.title('Comparison Mode: Trust & Confidence in London')

    # Define available dates and measures 
    available_dates = df_PAS_Borough['Date'].unique()
    available_measures = df_PAS_Borough['Measure'].unique()

    # Check if available_dates is empty
    if len(available_dates) == 0:
        st.error("No available dates found. Please check the data loading process.")
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_date_1 = st.select_slider('Select Date for Map 1', options=available_dates)
        selected_measure_1 = st.selectbox('Select Measure for Map 1', options=available_measures, key='measure1')

    with col2:
        selected_date_2 = st.select_slider('Select Date for Map 2', options=available_dates)
        selected_measure_2 = st.selectbox('Select Measure for Map 2', options=available_measures, key='measure2')

    col1.write("Map 1")
    with col1:
        st_map1 = display_map(df_PAS_Borough, selected_date_1, selected_measure_1, map_key="map1")

    col2.write("Map 2")
    with col2:
        st_map2 = display_map(df_PAS_Borough, selected_date_2, selected_measure_2, map_key="map2")

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Run the comparison page
comparison_page()
