import folium

import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly_express as px
import branca.colormap as cm

from typing import List
from streamlit_folium import st_folium




# DEFINE THE FUNCTIONS FOR HOMEPAGE 
    
def display_map_homepage(df: pd.DataFrame, date: str, measure: str, neighbourhoods_):
        
    # Filter data based on selected date
    filtered_data = df[(df['Measure'] == measure) & (df['Date'] == date)]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods_.merge(filtered_data, left_on='borough', right_on='Borough'))

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

    return st_folium(m, width=2000, height=1000)


def display_trend_measure_borough(df_: pd.DataFrame, borough_: str = None, measures_: List[str] = ['worries about crime near citizens']):
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




### DEFINE FUNCTIONS FOR CRIMEPAGE

def plot_barchart(df: pd.DataFrame, locat: str):
    fig = px.bar(df.groupby(by='Crime type').count().reset_index()[['Crime type','Month']].rename({'Month':'count'}, axis=1).sort_values(by='count', ascending=False), x='Crime type', y='count', title=f'Crimes in {locat}')

    # Update the layout to increase the title text size
    fig.update_layout(
        title={
            'text': f'Crimes in {locat}',
            'font': {
                'size': 24  # Set the title font size
            }
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def display_map_crimepage(df: pd.DataFrame, date: str, measure: str, neighbourhoods_):
        
    # Filter data based on selected date
    filtered_data = df[df['Date'] == date]

    # Merge the filtered data with the boroughs data
    merged_data = gpd.GeoDataFrame(neighbourhoods_.merge(filtered_data, left_on='borough', right_on='Borough'))

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

    return st_folium(m, width=2000, height=1000)

# Function to convert date format
def convert_date_format(date_str):
    return date_str[:7]  # Extract the first 7 characters (YYYY-MM)



### FUNCTIONS FOR RECOMMENDATIONS PAGE

#A function to calculate percentages for each ethnic group and borough
def calculate_percentages_recpage(df, question, values, ethnic_group, borough_column, ethnic_column):
    if question not in df.columns:
        return pd.DataFrame(columns=[borough_column, ethnic_column, 'Percentage'])
    
    if ethnic_group != 'All':
        df = df[df[ethnic_column] == ethnic_group]
    
    #We filter here the dataframe based on the question values
    filtered_df = df[df[question].isin(values)]
    
    #This is to count the total responses and filtered responses for each ethnic group within each borough
    total_counts = df.groupby([borough_column, ethnic_column]).size().rename('Total')
    disagree_counts = filtered_df.groupby([borough_column, ethnic_column]).size().rename('Disagree')
    
    #Combine and calculate percentages
    combined_counts = pd.concat([total_counts, disagree_counts], axis=1).fillna(0)
    combined_counts['Percentage'] = (combined_counts['Disagree'] / combined_counts['Total']) * 100
    combined_counts['Percentage'] = combined_counts['Percentage'].round(2)
    combined_counts = combined_counts.reset_index()
    
    return combined_counts[[borough_column, ethnic_column, 'Percentage']]

