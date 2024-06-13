# imports 
import os
import sys

import pandas as pd
import streamlit as st
import plotly.io as pio
import plotly.express as px

from streamlit_folium import st_folium

# Ensure the correct renderer is used for Streamlit
pio.renderers.default = "iframe"

# outer imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

# custom imports 
from app.app_func import display_map_crimepage, plot_barchart
from app.app_data_preprocessor import CRIMEPAGE_data, preprocess_neighbourhoods 

st.set_page_config(
    layout='wide',
    initial_sidebar_state='collapsed'
)



### RUN THE APPLICATION ### 

neighbourhoods = preprocess_neighbourhoods()
df_PAS_Crime, df_MET_Crime, df_PAS_Borough_Trust = CRIMEPAGE_data()

st.title("Crime Data in London")

# Slider for selecting date and selectbox for selecting the measure
available_dates = df_PAS_Borough_Trust['Date'].unique()
selected_date = st.sidebar.select_slider('Select Date', options=available_dates)

# Display the map with all crimes
st_map = display_map_crimepage(df=df_PAS_Borough_Trust, date=selected_date, measure='Trust MPS', neighbourhoods_=neighbourhoods)

# read the callback from map and return them
neighbourhood = ''
poly = ''
if st_map['last_active_drawing']:
    borough = st_map['last_active_drawing']['properties']['Borough']

    df_MET_Crime = df_MET_Crime[(df_MET_Crime['LSOA name'].str.contains(borough, na=False)) & (df_MET_Crime['Month'] == selected_date)].reset_index()
    df_PAS_Crime = df_PAS_Crime[(df_PAS_Crime['Borough'] == borough) & (df_PAS_Crime['Date'] == selected_date)].reset_index()

    # Convert the dictionary into a DataFrame
    try:
        data = eval(df_PAS_Crime['Crime type'].loc[0])
        # Extracting keys and values from the dictionary
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Count'])

        # Creating a bar chart using Plotly Express
        fig = px.bar(df, x='Category', y='Count', orientation='v', title=f'In {borough} People Are Afraid of:', 
                    labels={'Count': 'Counts', 'Category': 'Categories'})
        
        # Update the layout to increase the title text size
        fig.update_layout(
            title={
                'text': f'In {borough} People Are Afraid of:',
                'font': {
                    'size': 24  # Set the title font size
                }
            }
        )

        # Display the bar chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning('There is no PAS data for this time period, but there is Crime data from MET for this period')

    plot_barchart(df_MET_Crime, borough)



### AESTHETIC MODS ####

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




