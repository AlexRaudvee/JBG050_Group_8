# imports 
import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

# Ensure the correct renderer is used for Streamlit
pio.renderers.default = "iframe"

# outer imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# custom imports 
from functions.api_func import *
from app.home import df_PAS_Borough


# DEFINE FUNCTIONS

def plot_crime_map(df: pd.DataFrame, sample_size=10000):
    # Sample the data if it's too large
    if len(df) > sample_size:
        df = df.sample(sample_size)
    
    fig = px.scatter_mapbox(
        df, lat="Latitude", lon="Longitude", color="Crime type", hover_name="Location",
        hover_data=["Crime type", "Last outcome category", "Month"], zoom=10, height=600,
        title="Crime locations in London"
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

def plot_barchart(df: pd.DataFrame, locat: str):
    fig = px.bar(df.groupby(by='Crime type').count().reset_index()[['Crime type','Month']].rename({'Month':'count'}, axis=1).sort_values(by='count', ascending=False), x='Crime type', y='count', title=f'Crimes in {locat}')
    st.plotly_chart(fig, use_container_width=True)

# RUN THE APPLICATION

st.title("Crime Data in London")

# Define available dates and measures 
available_dates = df_PAS_Borough['Date'].unique()
available_measures = df_PAS_Borough['Measure'].unique()

# Slider for selecting date and selectbox for selecting the measure
selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

# Load all crime data files
data_dir = 'data/met_data'

# Check if the directory exists
if not os.path.exists(data_dir):
    st.error(f"Data directory '{data_dir}' does not exist.")
else:
    all_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('-metropolitan-street.csv'):
                all_files.append(os.path.join(root, file))

    # Check if there are any files to read
    if not all_files:
        st.error(f"No CSV files found in the directory '{data_dir}'.")
    else:
        df_list = [pd.read_csv(file) for file in all_files]

        # Check if there are any DataFrames to concatenate
        if not df_list:
            st.error("No dataframes to concatenate.")
        else:
            # Combine all dataframes into one
            df_all_years = pd.concat(df_list, ignore_index=True)

            # Display the map with all crimes
            plot_crime_map(df=df_all_years)

            # Optionally, display some statistics or other visualizations
            st.header("Crime Statistics")
            crime_counts = df_all_years['Crime type'].value_counts().reset_index()
            crime_counts.columns = ['Crime type', 'Count']
            st.dataframe(crime_counts)

            # Plot a bar chart of crime counts
            fig = px.bar(crime_counts, x='Crime type', y='Count', title='Total Crime Counts by Type')
            st.plotly_chart(fig, use_container_width=True)

### AESTHETIC MODS ####
st.set_page_config(
    page_title="Crime Data in London",
    layout="wide",
    initial_sidebar_state="collapsed",  # Collapse the sidebar
    page_icon='🔪'
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
        color: #4CAF50; /* Same as primaryColor */
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
        color: #4CAF50; /* Same as primaryColor */
    }

    /* Customizing the input widgets */
    .css-1cpxqw2 {
        font-family: 'Arial', sans-serif;
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
    </style>
    """,
    unsafe_allow_html=True
)




