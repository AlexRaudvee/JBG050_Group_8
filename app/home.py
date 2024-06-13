# imports 
import os
import sys
import subprocess

import pandas as pd
import streamlit as st

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# custom imports 
from functions.api_func import download_file
from app.app_func import display_map_homepage, display_box_ethnicity, display_trend_measure_borough
from app_data_preprocessor import HOMEPAGE_data, preprocess_neighbourhoods


### LOAD THE DATA IF IT IS NOT INSTALLED

# we run the preprocessor such to have needed csv
if not os.path.exists('data/pas_data_ward_level/pre_final.csv'):
    subprocess.run(["python", 'data_preprocessors/PAS_ward_level_preprocessor.py'])

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

neighbourhoods = preprocess_neighbourhoods()
df_perception, df_PAS_MPS, df_PAS_Borough, question_descriptions = HOMEPAGE_data()

### RUN THE APPLICATION
    
def run_app():
    """
    This function is the main entry point for the application. It sets up the Streamlit dashboard and loads the necessary data.
    """
    
    st.title('Trust & Confidence in London')

    # Define available dates and measures 
    available_dates = df_PAS_Borough['Date'].unique()
    available_measures = df_PAS_Borough['Measure'].unique()

    # Check if available_dates is empty
    if len(available_dates) == 0:
        st.error("No available dates found. Please check the data loading process.")
        return

    # Add buttons for different pages
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<a href="/comparison" target="_self"><button class="nav-button">Comparison Mode Page 🔎</button></a>', unsafe_allow_html=True)

    with col2:
        st.markdown('<a href="/crime" target="_self"><button class="nav-button">Crimes Page 🔪</button></a>', unsafe_allow_html=True)

    with col3:
        st.markdown('<a href="/responsiveness" target="_self"><button class="nav-button">Police Responsiveness Analysis Page 👮</button></a>', unsafe_allow_html=True)

    selected_date = st.select_slider('Select Date', options=available_dates,)# label_visibility='collapsed',)
    selected_measure = st.selectbox('Select Measure', options=available_measures)#, label_visibility='collapsed')
    selected_measures = st.multiselect('Select Measures for line plot', options=available_measures, default=selected_measure)#, label_visibility='collapsed')

    st_map = display_map_homepage(df_PAS_Borough, selected_date, selected_measure, neighbourhoods_=neighbourhoods)

    # read the callback from map and return them
    neighbourhood = ''
    poly = ''
    if st_map['last_active_drawing']:
        neighbourhood = st_map['last_active_drawing']['properties']['name']
        poly = st_map['last_active_drawing']['geometry']['coordinates']
        borough = st_map['last_active_drawing']['properties']['Borough']
        measure = st_map['last_active_drawing']['properties']['Measure']

        display_trend_measure_borough(df_=df_PAS_Borough, borough_=borough, measures_=selected_measures)
        display_box_ethnicity(df_=df_PAS_Borough, borough_=borough, measure_=selected_measure, date=selected_date)



### AESTHETIC MODS ####
st.set_page_config(
    page_title="Trust and Confidence in London",
    layout="wide",
    initial_sidebar_state="collapsed",  # Collapse the sidebar
    page_icon='🕵️‍♂️'
)

# Apply custom CSS for improved aesthetics
st.markdown(
    """
    <style>
    /* Customizing the title font and alignment */
    .css-18e3th9 {
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #466157; /* Same as primaryColor */
    }

    /* Customizing the main content area */
    .css-1d391kg {
        background-color: #F5F5F5;
        padding: 2rem;
        border-radius: 8px;
    }

    /* Customizing the sidebar */
    .css-1d391kg > div:nth-child(1) {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 8px;
    }

    /* Customizing the headers */
    .css-10trblm {
        font-family: 'Arial', sans-serif;
        color: #466157; /* Same as primaryColor */
    }

    /* Customizing the input widgets */
    .css-1cpxqw2 {
        font-family: 'Arial', sans-serif;
        color: #466157; /* Same as primaryColor */
    }

    /* Customizing the text elements */
    .css-2trqyj {
        color: #333333; /* Same as textColor */
    }

    /* Customizing the footers */
    footer {
        font-family: 'Arial', sans-serif;
        color: #333333; /* Same as textColor */
        text-align: center;
        padding: 1rem;
    }
    
    /* Horizontal menu styling */
    .horizontal-menu {
        display: flex;
        justify-content: center;
        list-style-type: none;
        padding: 0;
        background-color: #FFFFFF;
        margin-bottom: 20px;
    }

    .horizontal-menu li {
        margin: 0 15px;
    }

    .horizontal-menu a {
        text-decoration: none;
        color: #466157; /* Same as primaryColor */
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 18px;
    }

    .horizontal-menu a:hover {
        text-decoration: underline;
    }

    /* Button styling */
    .nav-button {
        width: 100%;
        background-color: #466157;
        color: white;
        padding: 10px;
        font-size: 16px;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .nav-button:hover {
        background-color: #3b514b;
    }

    /* Fullscreen map */
    .full-screen {
        height: calc(100vh - 100px); /* Full height minus some padding */
    }

    .stSelectbox [class*="css-"] {
        color: #466157; /* Same as primaryColor */
    }

    /* Select slider styling */
    .stSelectSlider .stSlider {
        color: #466157 !important;
    }

    .stSelectSlider .stSlider .stSlider__thumb {
        background-color: #466157 !important;
    }

    .stSelectSlider .stSlider .stSlider__track {
        background-color: #466157 !important;
    }

    /* Select box styling */
    .stSelectbox [class*="css-"] {
        color: #466157 !important;
    }

    .stSelectbox .st-bd {
        background-color: #F5F5F5 !important;
    }

    .stSelectbox .st-bg {
        background-color: #466157 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

run_app()
