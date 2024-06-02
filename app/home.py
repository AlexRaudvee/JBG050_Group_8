# imports 
import os
import sys
import folium
import subprocess

import pandas as pd
import seaborn as sns
import streamlit as st
import geopandas as gpd
import plotly_express as px
import branca.colormap as cm
import matplotlib.pyplot as plt

from typing import List
from streamlit_folium import st_folium

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# custom imports 
from config import DEV_EXPERIMENTAL, questions_dict
from functions.api_func import download_file, proportion_to_color

# LOAD THE DATA  

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

# renaming values
df_PAS_Borough.loc[df_PAS_Borough['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'
df_PAS_Borough.loc[df_PAS_Borough['Borough'] == 'Kensington & Chelsea', 'Borough'] = 'Kensington and Chelsea'
df_PAS_Borough.loc[df_PAS_Borough['Borough'] == 'Hammersmith & Fulham', 'Borough'] = 'Hammersmith and Fulham'
df_PAS_Borough.loc[df_PAS_Borough['Borough'] == 'Barking & Dagenham', 'Borough'] = 'Barking and Dagenham'

# decode the question number in to category: 
# Map the question names to their short descriptions
question_descriptions = {key: value[1] for key, value in questions_dict.items()}

# Rename the 'Measure' column in results_df using the question descriptions
df_PAS_Borough['Measure'] = df_PAS_Borough['Measure'].map(question_descriptions)

# load the neighbourhoods data 
neighbourhoods = gpd.read_file('data/neighbourhoods_boundary.geojson')


# DEFINE THE FUNCTIONS 
    
def display_map(df: pd.DataFrame, date: str, measure: str):
        
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

    return st_folium(m, width=1200, height=750)


def display_trend_measure_borough(borough_ = None, measures_: List[str] = ['worries about crime near citizens'], df_ = df_PAS_Borough):
    # filter the data only for need measure and borough
    filtered_data = df_[(df_['Borough'] == borough_) & (df_['Measure'].isin(measures_))]
    fig = px.line(filtered_data, x='Date', y='Total Proportion', color='Measure', title=f'Trend for measures in {borough_}')
    fig.update_layout(xaxis_rangeslider_visible=True)

    # display the line plot
    st.plotly_chart(fig, use_container_width=True)


def display_box_ethnicity(df_: pd.DataFrame, borough_: str, measure_: str, date: str):
    # Filter the data
    filtered_data = df_[(df_['Borough'] == borough_) & (df_['Measure'] == measure_) & (df_['Date'] == date)]
    
    # Extract proportions for each ethnicity
    proportions = filtered_data[['White_British_Proportion', 'White_Other_Proportion', 'Black_Proportion', 'Asian_Proportion', 'Mixed_Proportion', 'Other_Proportion']].values.flatten()
    ethnicities = ['White British', 'White Other', 'Black', 'Asian', 'Mixed', 'Other']
    
    # Create a DataFrame for plotting
    plot_data = pd.DataFrame({'Ethnicity': ethnicities * len(filtered_data), 'Proportion': proportions})
    
    # Plot the bar plot using Plotly Express
    fig = px.bar(plot_data, x='Ethnicity', y='Proportion', color='Ethnicity', barmode='group',
                 title=f"Bar Plot for {measure_} in {borough_} on {date}",
                 labels={'Ethnicity': 'Ethnicity', 'Proportion': 'Proportion'})
    
    # Customize layout
    fig.update_layout(xaxis=dict(tickangle=0, tickfont=dict(size=18)), yaxis=dict(range=[0, 1], tickfont=dict(size=18)), legend_title='Ethnicity', 
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(size=18))
    
    # Adjust the width of the bars
    fig.update_traces(marker=dict(line=dict(width=8)))
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)


# RUN THE APPLICATION
    
def run_app():
    """
    This function is the main entry point for the application. It sets up the Streamlit dashboard and loads the necessary data.
    """
    st.set_page_config(layout="wide",
                       page_title='Trust-Confidence UK',
                       page_icon='🕵️‍♂️')
    
    st.title('TRUST AND CONFIDENCE IN LONDON')

    # Define available dates and measures 
    available_dates = df_PAS_Borough['Date'].unique()
    available_measures = df_PAS_Borough['Measure'].unique()

    # Slider for selecting date and selectbox for selecting the measure
    selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
    selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

    # Selectbox for selecting multiple measures
    selected_measures = st.sidebar.multiselect('Select Measures for line plot', options=available_measures, default=selected_measure)

    try:
        st_map = display_map(df_PAS_Borough, selected_date, selected_measure)

        # read the callback from map and return them
        neighbourhood = ''
        poly = ''
        if st_map['last_active_drawing']:
            neighbourhood = st_map['last_active_drawing']['properties']['name']
            poly = st_map['last_active_drawing']['geometry']['coordinates']
            borough = st_map['last_active_drawing']['properties']['Borough']
            measure = st_map['last_active_drawing']['properties']['Measure']
        
        display_trend_measure_borough(borough, selected_measures, df_PAS_Borough)
        display_box_ethnicity(df_=df_PAS_Borough, borough_=borough, measure_=selected_measure, date=selected_date)
    except:
        pass
    
# run the application 
run_app()