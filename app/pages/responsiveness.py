# imports 
import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress

# outer imports
current = os.getcwd()
parent = os.path.dirname(current)
sys.path.append(parent)

from functions.api_func import *
from app.home import display_map, df_PAS_Borough, df_PAS_MPS

# DEFINE FUNCTIONS

def plot_barchart(df: pd.DataFrame, neighbourhood):
    fig = px.bar(df.groupby(by='category').count().reset_index()[['category','month']].rename({'month':'count'}, axis=1).sort_values(by='count', ascending=False), x='category', y='count', title=f'Crimes in {neighbourhood}')
    st.plotly_chart(fig, use_container_width=True)

def plot_scatter_with_regression(df, x_col, y_col, title):
    fig, ax = plt.subplots()
    sns.regplot(x=df[x_col], y=df[y_col], ax=ax)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    slope, intercept, r_value, p_value, std_err = linregress(df[x_col], df[y_col])
    ax.set_title(f"{title}\nR-squared: {r_value**2:.2f}, p-value: {p_value:.2e}")
    st.pyplot(fig)

def create_multi_axis_plot(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # traces for each measure
    measures = ["Listen to concerns", "Relied on to be there", "Understand issues"]
    for measure in measures:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df[measure],
                mode='markers',
                name=measure,
                hoverinfo='x+y',
                text=df['Borough'],
                marker=dict(size=10)
            ),
            secondary_y=False,
        )
        
        # regression lines
        slope, intercept, r_value, p_value, std_err = linregress(df[measure], df["Trust MPS"])
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=slope * df[measure] + intercept,
                mode='lines',
                name=f'{measure} Regression Line',
                line=dict(dash='dash')
            ),
            secondary_y=False,
        )

    # Trust MPS trace
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Trust MPS'],
            mode='lines+markers',
            name='Trust MPS',
            hoverinfo='x+y',
            marker=dict(size=10, color='rgba(152, 0, 0, .8)')
        ),
        secondary_y=True,
    )

    # figure title and layout
    fig.update_layout(
        title_text='Multi-Axis Interactive Plot: Police Responsiveness and Trust MPS',
        xaxis_title='Date',
        yaxis_title='Proportion',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    fig.update_yaxes(title_text="Responsiveness Measures", secondary_y=False)
    fig.update_yaxes(title_text="Trust MPS", secondary_y=True)

    return fig

# RUN THE APPLICATION

st.title("Police Responsiveness and Trust Analysis")

# Filter data for relevant measures regarding SubQuestion 3 *Pablo
relevant_measures = ["Listen to concerns", "Relied on to be there", "Understand issues", "Trust MPS"]
df_relevant_mps = df_PAS_MPS[df_PAS_MPS['Measure'].isin(relevant_measures)]
df_relevant_borough = df_PAS_Borough[df_PAS_Borough['Measure'].isin(relevant_measures)]

# Pivot the data to have measures as columns
df_mps_pivot = df_relevant_mps.pivot_table(index=["Date", "Borough"], columns="Measure", values="Proportion").reset_index()
df_borough_pivot = df_relevant_borough.pivot_table(index=["Date", "Borough"], columns="Measure", values="Proportion").reset_index()
numeric_columns_mps = df_mps_pivot.select_dtypes(include=['float64', 'int64']).columns
numeric_columns_borough = df_borough_pivot.select_dtypes(include=['float64', 'int64']).columns

# Merge dataframes for combined analysis
df_combined = pd.merge(df_mps_pivot, df_borough_pivot, on=["Date", "Borough"], suffixes=('_MPS', '_Borough'))

# Correlation between Trust MPS and other measures
correlation_mps = df_mps_pivot[numeric_columns_mps].corr()
correlation_borough = df_borough_pivot[numeric_columns_borough].corr()

st.write("Correlation matrix for MPS DataFrame:")
st.dataframe(correlation_mps)

st.write("Correlation matrix for Borough DataFrame:")
st.dataframe(correlation_borough)

# Scatter plot for visualization
scatter_plot_data = df_mps_pivot.dropna(subset=["Trust MPS"])

for measure in ["Listen to concerns", "Relied on to be there", "Understand issues"]:
    if measure in scatter_plot_data.columns:
        st.subheader(f"Scatter plot for Trust MPS vs {measure}")
        scatter_data = scatter_plot_data[["Trust MPS", measure]]
        st.scatter_chart(scatter_data)

# Scatter plot with regression line using seaborn
for measure in ["Listen to concerns", "Relied on to be there", "Understand issues"]:
    if measure in scatter_plot_data.columns:
        plot_scatter_with_regression(scatter_plot_data, measure, "Trust MPS", f"Trust MPS vs {measure}")

# Define available dates and measures 
available_dates = df_PAS_Borough['Date'].unique()
available_measures = df_PAS_Borough['Measure'].unique()

# Slider for selecting date and selectbox for selecting the measure
selected_date = st.sidebar.select_slider('Select Date', options=available_dates)
selected_measure = st.sidebar.selectbox('Select Measure', options=available_measures)

st_map = display_map(df_PAS_Borough, selected_date, selected_measure)

# Read the callback from map and return them
neighbourhood = ''
poly = []
if st_map['last_active_drawing']:
    neighbourhood = st_map['last_active_drawing']['properties']['name']
    poly = st_map['last_active_drawing']['geometry']['coordinates']
    borough = st_map['last_active_drawing']['properties']['Borough']
    measure = st_map['last_active_drawing']['properties']['Measure']

if poly:
    plot_barchart(df=pd.DataFrame(extract_street_level_crimes(date=selected_date, poly=poly[0])), neighbourhood=neighbourhood)

# Create the multi-axis plot
multi_axis_fig = create_multi_axis_plot(df_mps_pivot)

# Display the plot in Streamlit
st.plotly_chart(multi_axis_fig, use_container_width=True)
