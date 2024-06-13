# imports 
import os 
import sys 

import pandas as pd 
import streamlit as st
import plotly.express as px

from streamlit_folium import st_folium

# modifying the root path for imports
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent) 

from app.app_func import calculate_percentages_recpage, display_map_crimepage
from app.app_data_preprocessor import RECOMMENDATIONPAGE_data, preprocess_neighbourhoods



### RUN THE APPLICATION

st.set_page_config(
    layout='wide',
    initial_sidebar_state='expanded'
)

neighbourhoods = preprocess_neighbourhoods()

csv_files, borough_column_mapping, ethnic_group_column_mapping, questions, df_PAS_Borough_Trust = RECOMMENDATIONPAGE_data()

# Initialize the Streamlit app
st.title("Borough Recommendation System")

# Year selection dropdown
selected_year = st.sidebar.selectbox('Select Year', options=list(csv_files.keys()), index=0)

# Question selection dropdown
selected_question = st.sidebar.selectbox('Select Question', options=[q for q in questions.keys()], format_func=lambda q: questions[q]['statement'])

# Ethnicity selection dropdown
selected_ethnicity = st.sidebar.selectbox('Select Ethnicity', options=['All'] + list(pd.read_csv(csv_files[selected_year])[ethnic_group_column_mapping[selected_year]].dropna().unique()))

# Top/Bottom selection radio buttons
top_bottom = st.sidebar.radio('Top/Bottom Percentages', options=['top', 'bottom'], index=0)

if selected_year == '20-21':
    selected_date = '2021-12'
elif selected_year == '19-20':
    selected_date = '2020-12'
elif selected_year == '18-19':
    selected_date = '2019-12'
elif selected_year == '17-18':
    selected_date = '2018-12'
elif selected_year == '15-17':
    selected_date = '2017-12'

# Load the data for the selected year
df = pd.read_csv(csv_files[selected_year])

st_map = display_map_crimepage(df=df_PAS_Borough_Trust, date=selected_date, measure='Trust MPS', neighbourhoods_=neighbourhoods)


if st_map['last_active_drawing']:
    selected_borough = st_map['last_active_drawing']['properties']['Borough']


    # Rename the borough and ethnic group columns if necessary
    borough_column = borough_column_mapping[selected_year]
    ethnic_column = ethnic_group_column_mapping[selected_year]
    if borough_column != 'Borough':
        df = df.rename(columns={borough_column: 'Borough'})
    if ethnic_column != 'ReNQ147':
        df = df.rename(columns={ethnic_column: 'ReNQ147'})

    # Calculate percentages based on selected question, borough, and ethnicity
    percentages_df = calculate_percentages_recpage(df, selected_question, questions[selected_question]['values'], selected_ethnicity, 'Borough', 'ReNQ147')

    if percentages_df.empty:
        st.write("Question not available for the selected year.")
    else:
        if selected_borough == 'All':
            borough_percentages = percentages_df.sort_values(by='Percentage')
        else:
            borough_percentages = percentages_df[percentages_df['Borough'] == selected_borough].sort_values(by='Percentage')
        
        if selected_ethnicity != 'All':
            borough_percentages = borough_percentages[borough_percentages['ReNQ147'] == selected_ethnicity]

        if selected_borough == 'All' and selected_ethnicity == 'All':
            fig = px.bar(borough_percentages, x='Borough', y='Percentage', color='ReNQ147', barmode='group', title=questions[selected_question]['statement'],
                        hover_data={'ReNQ147': False, 'Percentage': True}, labels={'ReNQ147': 'Ethnic group'})
        elif selected_borough == 'All':
            fig = px.bar(borough_percentages, x='Borough', y='Percentage', title=questions[selected_question]['statement'],
                        hover_data={'ReNQ147': False, 'Percentage': True}, labels={'ReNQ147': 'Ethnic group'})
        else:
            if selected_ethnicity == 'All':
                fig = px.bar(borough_percentages, x='ReNQ147', y='Percentage', title=questions[selected_question]['statement'],
                            hover_data={'ReNQ147': False, 'Percentage': True}, labels={'ReNQ147': 'Ethnic group'})
            else:
                if top_bottom == 'top':
                    top_boroughs = percentages_df[(percentages_df['ReNQ147'] == selected_ethnicity)].nsmallest(5, 'Percentage')
                else:
                    top_boroughs = percentages_df[(percentages_df['ReNQ147'] == selected_ethnicity)].nlargest(5, 'Percentage')
                
                selected_borough_data = percentages_df[(percentages_df['Borough'] == selected_borough) & (percentages_df['ReNQ147'] == selected_ethnicity)]
                comparison_data = pd.concat([top_boroughs, selected_borough_data]).drop_duplicates().sort_values(by='Percentage')
                
                fig = px.bar(comparison_data, x='Borough', y='Percentage', title=questions[selected_question]['statement'],
                            hover_data={'ReNQ147': False, 'Percentage': True}, labels={'ReNQ147': 'Ethnic group'})
                
                fig.update_traces(marker_color=['red' if borough == selected_borough else '#636EFA' for borough in comparison_data['Borough']])

                # Update the layout to increase the title text size
                fig.update_layout(
                    title={
                        'text': questions[selected_question]['statement'],
                        'font': {
                            'size': 24  # Set the title font size
                        }
                    }
                )

        st.plotly_chart(fig, use_container_width=True)

        if selected_borough != 'All' and selected_ethnicity != 'All':
            all_boroughs_sorted = percentages_df[percentages_df['ReNQ147'] == selected_ethnicity].sort_values(by='Percentage')
            selected_borough_rank = all_boroughs_sorted.reset_index().index[all_boroughs_sorted['Borough'] == selected_borough][0] + 1
            num_boroughs = len(all_boroughs_sorted)
            
            top_3_boroughs = all_boroughs_sorted.head(3)['Borough'].tolist()
            if selected_borough in top_3_boroughs:
                if selected_borough == top_3_boroughs[0]:
                    advice = f"{selected_borough} is the best performing borough for the selected ethnic group."
                else:
                    better_boroughs = [b for b in top_3_boroughs if b != selected_borough]
                    advice = f"{selected_borough} is among the top 3 performing boroughs. Consider getting advice from {', '.join(better_boroughs)}."
            else:
                advice = f"{selected_borough} is not in the top 3 performing boroughs. Consider getting advice from {', '.join(top_3_boroughs)}."

            rank_text = f"{selected_borough} ranks {selected_borough_rank} out of {num_boroughs} boroughs for the selected ethnic group."
            st.write(f'#### {advice}')
            st.write(f'#### {rank_text}')