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

st.set_page_config(
    page_title='Trust to Crime',
    page_icon='🔪',
    layout='wide'
)

st.title("Here is going to be the crime data")

# # Define available dates and measures 
# available_dates = df_PAS_Borough['Date'].unique()
# available_measures = df_PAS_Borough['Measure'].unique()

# # Slider for selecting date and selectbox for selecting the measure
# selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
# selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

# st_map = display_map(df_PAS_Borough, selected_date, selected_measure)

# # read the callback from map and return them
# neighbourhood = ''
# poly = None
# chosen_borough_on_map = None
# if st_map['last_active_drawing']:
#     neighbourhood_on_map = st_map['last_active_drawing']['properties']['name']
#     poly_on_map = st_map['last_active_drawing']['geometry']['coordinates']
#     chosen_borough_on_map = st_map['last_active_drawing']['properties']['Borough']
#     measure_on_map = st_map['last_active_drawing']['properties']['Measure']

# # React on the callbacks 
# try:
#     # load the needed dataframe 
#     df = pd.read_csv(f'data/met_data/{selected_date}/{selected_date}-metropolitan-street.csv')

#     #filter rows
#     result_df = df[df['LSOA name'].str[:-5] == chosen_borough_on_map]

#     # plot the bar chart
#     plot_barchart(df=result_df, locat=chosen_borough_on_map)

#     # plot the crime map
#     plot_crime_map(df=result_df, date=selected_date, measure=chosen_borough_on_map)

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

# # Rise an error (dev option)
# except:
#     st.warning("""The application is still in developing stage,
#             and for some neighbourhoods we cannot extract 
#             the data due to limit of charaters in the request 
#             to database of the London MPS. (We are working on 
#             it right now)""")












