# imports 
import os
import sys

import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from scipy.stats import linregress
from plotly.subplots import make_subplots

# outer imports
current = os.getcwd()
parent = os.path.dirname(current)
sys.path.append(parent)

# custom imports
from app.home import df_PAS_Borough, df_PAS_MPS

# DEFINE FUNCTIONS

def plot_barchart(df: pd.DataFrame, neighbourhood):
    fig = px.bar(df.groupby(by='category').count().reset_index()[['category','month']].rename({'month':'count'}, axis=1).sort_values(by='count', ascending=False), x='category', y='count', title=f'Crimes in {neighbourhood}')
    st.plotly_chart(fig, use_container_width=True)

def plot_scatter_with_regression(df, x_col, y_col, title):
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(df[x_col], df[y_col])
    r_squared = r_value**2

    # Create the regression line
    df['Regression'] = slope * df[x_col] + intercept

    # Create scatter plot with regression line using Plotly Express
    fig = px.scatter(df, x=x_col, y=y_col, title=title)
    fig.add_traces(px.line(df, x=x_col, y='Regression').data)

    # Update layout with R-squared and p-value
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        annotations=[dict(
            xref='paper', yref='paper', x=0.5, y=-0.2,
            showarrow=False, text=f"R-squared: {r_squared:.2f}, p-value: {p_value:.2e}"
        )]
    )

    st.plotly_chart(fig)

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

st.set_page_config(layout="wide",
                       page_title='Responsiveness UK',
                       page_icon='🕵️‍♂️')

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

selected_measure = st.selectbox('Select Measure', options=["Listen to concerns", "Relied on to be there", "Understand issues"])

st.write(selected_measure)
st.subheader(f"Scatter plot for Trust MPS vs {selected_measure}")
scatter_data = scatter_plot_data[["Trust MPS", selected_measure]]
scatter_plot = px.scatter(scatter_data)
st.plotly_chart(scatter_plot)

plot_scatter_with_regression(scatter_plot_data, selected_measure, "Trust MPS", f"Trust MPS vs {selected_measure}")

# Create the multi-axis plot
multi_axis_fig = create_multi_axis_plot(df_mps_pivot)

# Display the plot in Streamlit
st.plotly_chart(multi_axis_fig, use_container_width=True)
