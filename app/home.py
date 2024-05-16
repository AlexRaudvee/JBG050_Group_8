# imports 
import os
import sys
import time
import json
import folium
import geojson
import requests

import pandas as pd
import pydeck as pdk
import streamlit as st
import geopandas as gpd
import branca.colormap as cm
import streamlit.components.v1 as components
import plotly_express as px

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

from streamlit_folium import st_folium
from typing import List
from folium.features import GeoJsonTooltip
from functions.api_func import download_file, proportion_to_color
from config import DEV_EXPERIMENTAL

# LOAD THE DATA  

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
df_PAS_Borough = pd.read_csv(f'{path_to_PAS}_Borough.csv')

# Preprocess the data fro MPS
df_PAS_MPS['Date'] = df_PAS_MPS['Date'].apply(lambda x: x[:4])

# Preprocess the data for Borough
df_PAS_Borough = df_PAS_Borough.loc[:, ~df_PAS_Borough.columns.str.contains('^Unnamed')]
df_PAS_Borough = df_PAS_Borough.dropna(axis=1, how='all')
df_PAS_Borough['Date'] = df_PAS_Borough['Date'].apply(lambda x: x[:7])
df_PAS_Borough['Borough'] = df_PAS_Borough['Borough'].apply(lambda x: 'Westminster' if x == 'City of Westminster' else x)
df_PAS_Borough.loc[df_PAS_Borough['Borough'] == 'Richmond Upon Thames', 'Borough'] = 'Richmond upon Thames'

# load the neighbourhoods data 
neighbourhoods = gpd.read_file('data/neighbourhoods_boundary.geojson')


# DEFINE THE FUNCTIONS 
    
def display_map(df: pd.DataFrame, date: str, measure: str):
        
    # Filter data based on selected date
    filtered_data = df[(df['Measure'] == measure) & (df['Date'] == date)]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods.merge(filtered_data, left_on='borough', right_on='Borough'))

    # create the color map 
    linear = cm.LinearColormap(["red", "yellow", "green"], vmin=min(merged_data['Proportion']), vmax=max(merged_data['Proportion']))
    # create the map
    m = folium.Map(location=[51.5074, -0.1278], tiles="Cartodb Positron", zoom_start=10.5)

    # geojson layer for the map
    geojson_layer = folium.features.GeoJson(
            data=merged_data,
            style_function=lambda feature: {
                "fillColor": linear(feature['properties']['Proportion']),
                "color": "black",
                "weight": 1,
                "dashArray": "5, 5",
            },
            tooltip=folium.features.GeoJsonTooltip(fields=['borough', 'name', 'Proportion'],
                                                    aliases=['Borough', 'Location', 'Proportion']))
    # add layer to the map
    geojson_layer.add_to(m)

    # define the callback 

    return st_folium(m, width=1200, height=750)


def display_trend_measure_borough(borough_ = None, neighbour_ = None, measures_: List[str] = ['Understand issues'], df_ = df_PAS_Borough):
    # filter the data only for need measure and borough
    filtered_data = df_[(df_['Borough'] == borough_) & (df_['Measure'].isin(measures_))]
    fig = px.line(filtered_data, x='Date', y='Proportion', color='Measure', title=f'Trend for measures in {borough_}')
    fig.update_layout(xaxis_rangeslider_visible=True)

    # display the line plot
    st.plotly_chart(fig, use_container_width=True)

def display_trend_perception(measures_: List[str] = ['Agree the police are dealing with the things that matter to this community'], df_ = df_perception):
    # filter the data only for need measure and borough
    df_ = df_[df_['measure'].isin(measures_)]
    fig = px.line(df_, x='date', y='proportion', color='measure', title=f'Trend for perceptions in London')

    # Update layout to adjust legend
    fig.update_layout(
        xaxis_rangeslider_visible=True,
        legend=dict(
            orientation="h",  # horizontal orientation
            yanchor="top",
            y=1.8,
            xanchor="right",
            x=1
        )
    )

    # Update legend font size
    fig.update_layout(legend=dict(font=dict(size=10)))

    # display the line plot
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
    avaliable_perceptions = df_perception['measure'].unique()

    # selectbox for selection multiple measures for line plot about perception of police
    selected_measures_perception = st.sidebar.multiselect('Select perceptions for line plot', options=avaliable_perceptions, default=avaliable_perceptions[0])

    # Slider for selecting date and selectbox for selecting the measure
    selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
    selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

    # Selectbox for selecting multiple measures
    selected_measures = st.sidebar.multiselect('Select Measures for line plot', options=available_measures, default=selected_measure)

    try:

        display_trend_perception(selected_measures_perception, df_perception)

        st_map = display_map(df_PAS_Borough, selected_date, selected_measure)

        # read the callback from map and return them
        neighbourhood = ''
        poly = ''
        if st_map['last_active_drawing']:
            neighbourhood = st_map['last_active_drawing']['properties']['name']
            poly = st_map['last_active_drawing']['geometry']['coordinates']
            borough = st_map['last_active_drawing']['properties']['Borough']
            measure = st_map['last_active_drawing']['properties']['Measure']
        
        display_trend_measure_borough(borough, neighbourhood, selected_measures, df_PAS_Borough)
        
    except:
        pass
    


# run the application 
run_app()