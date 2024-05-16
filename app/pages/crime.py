# imports 
import os
import sys

import pandas as pd
import streamlit as st
import plotly_express as px

# outer imports
current = os.getcwd()
parent = os.path.dirname(current)
sys.path.append(parent)

from functions.api_func import *
from app.home import display_map, df_PAS_Borough

# DEFINE FUNCTIONS

def plot_barchart(df: pd.DataFrame, neighbourhood):
    fig = px.bar(df.groupby(by='category').count().reset_index()[['category','month']].rename({'month':'count'}, axis=1).sort_values(by='count', ascending=False), x='category', y='count', title=f'Crimes in {neighbourhood}')

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
poly = ''
if st_map['last_active_drawing']:
    neighbourhood = st_map['last_active_drawing']['properties']['name']
    poly = st_map['last_active_drawing']['geometry']['coordinates']
    borough = st_map['last_active_drawing']['properties']['Borough']
    measure = st_map['last_active_drawing']['properties']['Measure']

plot_barchart(df=pd.DataFrame(extract_street_level_crimes(date=selected_date, poly=poly[0])), neighbourhood=neighbourhood)