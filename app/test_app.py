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

# modifing the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

from ipyleaflet import Marker
from folium.features import GeoJson, GeoJsonTooltip
from branca.element import MacroElement
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
    
if not os.path.exists(f'{save_directory}/PAS_T%26Cdashboard_to%20Q3%2023-24_Borough.csv' ):
    df = pd.read_excel(f'{path_to_PAS}.xlsx', sheet_name='Borough', header=0)
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)
    df = pd.read_csv(f'{path_to_PAS}_Borough.csv')
    df.to_csv(f'{path_to_PAS}_Borough.csv', index=False)


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

def add_click_callback(m, merged_data):
    """Add click callback to Folium map"""
    callback = """
        function (e) {
            var layer = e.target;
            var name = layer.feature.properties.name;
            var output = document.getElementById('borough_output');
            output.innerHTML = "Clicked Borough: " + name;
        }
    """
    m.add_child(folium.ClickForMarker(popup=f''))
    m.get_root().html.add_child(folium.Element(f'<script>{callback}</script>'))






# set the app of the dashboard
def app_():
    st.title('London Neighbourhoods Map')

    # test features
    DATE = '2023-12'
    MEASURE = 'Understand issues'

    neighbourhoods = gpd.read_file('data/neighbourhoods_boundary.geojson')

    # Define available dates and measures 
    available_dates = df_PAS_Borough['Date'].unique()
    available_measures = df_PAS_Borough['Measure'].unique()


    # Slider for selecting date and selectbox for selecting the measure
    selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
    selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

    # Filter data based on selected date
    filtered_data = df_PAS_Borough[(df_PAS_Borough['Measure'] == selected_measure) & (df_PAS_Borough['Date'] == selected_date)]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods.merge(filtered_data, left_on='borough', right_on='Borough'))

    # Define the base map
    pydeck_map = pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=51.5074,
            longitude=-0.1278,
            zoom=9,
            pitch=0
        ),
        map_style="mapbox://styles/mapbox/outdoors-v12",
        # Add tooltip to display proportion value
        tooltip = {
            "html": "<b>Borough:</b> {borough} <br> <b>Location:</b> {name} <br/> <b>Proportion:</b> {Proportion} <br/> ",
            "style": {
                    "backgroundColor": "#E4FCF7",
                    "color": "black"}}
    )


    # Add the layer with the proportion colors and the edges of the boroughs
    pydeck_map.layers.append(pdk.Layer(
        "GeoJsonLayer",
        data=merged_data,
        get_fill_color=["255 - 255 * Proportion", "255 * Proportion", 0, 200],
        get_line_color=[0, 0, 0],
        get_line_width=10,
        pickable=True,
        auto_highlight=True,
    ))

    # Display the map
    map_container = st.pydeck_chart(pydeck_map)

    ########### Other experiment IT IS ONLY FOR DEVELOPMENT BY ALEX ###########

    if DEV_EXPERIMENTAL:
        # Create a color scale for the proportion
        linear = cm.LinearColormap(["red", "yellow", "green"], vmin=min(merged_data['Proportion']), vmax=max(merged_data['Proportion']))

        # Create a map
        m = folium.Map(location=[51.5074, -0.1278], tiles="cartodbpositron", zoom_start=10)

        # Add a GeoJson layer to the map
        GeoJson(
            data=merged_data,
            style_function=lambda feature: {
                "fillColor": linear(feature['properties']['Proportion']),
                "color": "black",
                "weight": 1,
                "dashArray": "5, 5",
            },
            tooltip=GeoJsonTooltip(fields=['borough', 'name', 'Proportion'],
                                                    aliases=['Borough', 'Location', 'Proportion'])
        ).add_to(m)

        linear.caption = f"Proportion of {selected_measure}"
        m.add_child(linear)

        # Add a click event handler to the map
        def click_handler(event=None, **kwargs):
            clicked = on_map_click(kwargs, m)
            if clicked is not None:
                print("Clicked points:", clicked)

        m.on_interaction(click_handler)
        # Add click callback to Folium map
        add_click_callback(m, merged_data)

        components.html(m._repr_html_(), height=500, scrolling=True)

        st.write("<div id='borough_output'></div>", unsafe_allow_html=True)

# run the application 
def app_():
    """
    This function is the main entry point for the application. It sets up the Streamlit dashboard and loads the necessary data.
    """
    st.title('London Neighbourhoods Map')

    # test features
    DATE = '2023-12'
    MEASURE = 'Understand issues'

    neighbourhoods = gpd.read_file('data/neighbourhoods_boundary.geojson')

    # Define available dates and measures 
    available_dates = df_PAS_Borough['Date'].unique()
    available_measures = df_PAS_Borough['Measure'].unique()


    # Slider for selecting date and selectbox for selecting the measure
    selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
    selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

    # Filter data based on selected date
    filtered_data = df_PAS_Borough[(df_PAS_Borough['Measure'] == selected_measure) & (df_PAS_Borough['Date'] == selected_date)]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods.merge(filtered_data, left_on='borough', right_on='Borough'))

    # Define the base map
    pydeck_map = pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=51.5074,
            longitude=-0.1278,
            zoom=9,
            pitch=0
        ),
        map_style="mapbox://styles/mapbox/outdoors-v12",
        # Add tooltip to display proportion value
        tooltip = {
            "html": "<b>Borough:</b> {borough} <br> <b>Location:</b> {name} <br/> <b>Proportion:</b> {Proportion} <br/> ",
            "style": {
                    "backgroundColor": "#E4FCF7",
                    "color": "black"}}
    )


    # Add the layer with the proportion colors and the edges of the boroughs
    pydeck_map.layers.append(pdk.Layer(
        "GeoJsonLayer",
        data=merged_data,
        get_fill_color=["255 - 255 * Proportion", "255 * Proportion", 0, 200],
        get_line_color=[0, 0, 0],
        get_line_width=10,
        pickable=True,
        auto_highlight=True,
    ))

    # Display the map
    map_container = st.pydeck_chart(pydeck_map)

    ########### Other experiment IT IS ONLY FOR DEVELOPMENT BY ALEX ###########

    if DEV_EXPERIMENTAL:
        # Create a color scale for the proportion
        linear = cm.LinearColormap(["red", "yellow", "green"], vmin=min(merged_data['Proportion']), vmax=max(merged_data['Proportion']))

        # Create a map
        m = folium.Map(location=[51.5074, -0.1278], tiles="cartodbpositron", zoom_start=10)

        # Add a GeoJson layer to the map
        GeoJson(
            data=merged_data,
            style_function=lambda feature: {
                "fillColor": linear(feature['properties']['Proportion']),
                "color": "black",
                "weight": 1,
                "dashArray": "5, 5",
            },
            tooltip=GeoJsonTooltip(fields=['borough', 'name', 'Proportion'],
                                                    aliases=['Borough', 'Location', 'Proportion'])
        ).add_to(m)

        linear.caption = f"Proportion of {selected_measure}"
        m.add_child(linear)

        # Add a click event handler to the map
        def click_handler(event=None, **kwargs):
            clicked = on_map_click(kwargs, m)
            if clicked is not None:
                print("Clicked points:", clicked)

        m.on_interaction(click_handler)
        # Add click callback to Folium map
        add_click_callback(m, merged_data)

        components.html(m._repr_html_(), height=500, scrolling=True)

        st.write("<div id='borough_output'></div>", unsafe_allow_html=True)
app_()