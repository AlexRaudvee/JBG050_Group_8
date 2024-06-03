# imports 
import os
import sys

import pandas as pd
import streamlit as st
import plotly_express as px

# outer imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# custom imports 
from functions.api_func import *
from app.home import display_map, df_PAS_Borough


# DEFINE FUNCTIONS

def plot_barchart(df: pd.DataFrame, locat: str):
    fig = px.bar(df.groupby(by='Crime type').count().reset_index()[['Crime type','Month']].rename({'Month':'count'}, axis=1).sort_values(by='count', ascending=False), x='Crime type', y='count', title=f'Crimes in {locat}')

    # display the line plot
    st.plotly_chart(fig, use_container_width=True)

# RUN THE APPLICATION

st.set_page_config(
    page_title='Trust to Crime',
    page_icon='🔪',
    layout='wide'
)

st.title("Here is going to be the crime data")

# Define available dates and measures 
available_dates = df_PAS_Borough['Date'].unique()
available_measures = df_PAS_Borough['Measure'].unique()

# Slider for selecting date and selectbox for selecting the measure
selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

st_map = display_map(df_PAS_Borough, selected_date, selected_measure)

# read the callback from map and return them
neighbourhood = ''
poly = None
chosen_borough_on_map = None
if st_map['last_active_drawing']:
    neighbourhood_on_map = st_map['last_active_drawing']['properties']['name']
    poly_on_map = st_map['last_active_drawing']['geometry']['coordinates']
    chosen_borough_on_map = st_map['last_active_drawing']['properties']['Borough']
    measure_on_map = st_map['last_active_drawing']['properties']['Measure']

# React on the callbacks 
try:
    # load the needed dataframe 
    df = pd.read_csv(f'data/met_data/{selected_date}/{selected_date}-metropolitan-street.csv')

    #filter rows
    result_df = df[df['LSOA name'].str[:-5] == chosen_borough_on_map]

    # plot the bar chart
    plot_barchart(df=result_df, locat=chosen_borough_on_map)

# Rise an error (dev option)
except:
    st.warning("""The application is still in developing stage,
            and for some neighbourhoods we cannot extract 
            the data due to limit of charaters in the request 
            to database of the London MPS. (We are working on 
            it right now)""")
