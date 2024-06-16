# imports 
import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress
from plotly.subplots import make_subplots

# Custom CSS for matching the presentation style
st.set_page_config(
    layout='wide',
    initial_sidebar_state='expanded'
)
st.markdown(
    """
    <style>
    /* Customizing the title font and alignment */
    .css-18e3th9 {
        text-align: center;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #466157; /* Title color */
    }

    /* Customizing the main content area */
    .css-1d391kg {
        background-color: #F5F5F5; /* Light background */
        padding: 2rem;
        border-radius: 8px;
    }

    /* Customizing the sidebar */
    .css-1d391kg > div:nth-child(1) {
        background-color: #FFFFFF; /* White background */
        padding: 2rem;
        border-radius: 8px;
    }

    /* Customizing the headers */
    .css-10trblm {
        font-family: 'Arial', sans-serif;
        color: #466157; /* Header color */
    }

    /* Customizing the input widgets */
    .css-1cpxqw2 {
        font-family: 'Arial', sans-serif;
    }

    /* Customizing the text elements */
    .css-2trqyj {
        color: #333333; /* Dark text color */
    }

    /* Customizing the footers */
    footer {
        font-family: 'Arial', sans-serif;
        color: #333333; /* Dark text color */
        text-align: center;
        padding: 1rem;
    }

    /* Style for plots */
    .css-1lcbmhc {
        margin: 20px;
    }

    /* Custom button */
    .css-1x8cf1d {
        background-color: #3D4F45; /* Button background color */
        color: #FFFFFF; /* Button text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.title("Police Responsiveness and Trust Analysis")

# outer imports
current = os.getcwd()
parent = os.path.dirname(current)
sys.path.append(parent)

# custom imports
from app.app_data_preprocessor import RESPPONSIVNESSPAGE_data


# DEFINE FUNCTIONS

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
        )],
        title_font=dict(size=20, color='#466157')  # Title font color
    )

    st.plotly_chart(fig, use_container_width=True)

def create_multi_axis_plot(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # traces for each measure
    measures = ["Listen to concerns", "Relied on to be there", "Understand issues"]
    for measure in measures:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df[measure],
                mode='markers+lines',
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
        title_font=dict(size=20, color='#466157'),  # Title font color
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    fig.update_yaxes(title_text="Responsiveness Measures", secondary_y=False)
    fig.update_yaxes(title_text="Trust MPS", secondary_y=True)

    # # Highlight the period after the start of the pandemic
    # fig.add_vrect(
    #     x0='2020-03', x1=df['Date'].max(),
    #     fillcolor="LightSalmon", opacity=0.3,
    #     layer="below", line_width=0,
    #     annotation_text="Pandemic Period", annotation_position="top left"
    # )

    return fig



### LOAD THE DATA

df_PAS_MPS, df_PAS_Borough, question_descriptions = RESPPONSIVNESSPAGE_data()



# Filter data for relevant measures
relevant_measures = ["Listen to concerns", "Relied on to be there", "Understand issues", "Trust MPS"]
df_relevant_mps = df_PAS_MPS
df_relevant_borough = df_PAS_Borough

# Use the correct column names for pivot table
pivot_column_mps = 'Proportion'
pivot_column_borough = 'Total Proportion'

# Pivot the data to have measures as columns
df_mps_pivot = df_relevant_mps.pivot_table(index=["Date", "Borough"], columns="Measure", values=pivot_column_mps).reset_index()
df_borough_pivot = df_relevant_borough.pivot_table(index=["Date", "Borough"], columns="Measure", values=pivot_column_borough).reset_index()

numeric_columns_mps = df_mps_pivot.select_dtypes(include=['float64', 'int64']).columns
numeric_columns_borough = df_borough_pivot.select_dtypes(include=['float64', 'int64']).columns

# Merge dataframes for combined analysis
df_combined = pd.merge(df_mps_pivot, df_borough_pivot, on=["Date", "Borough"], suffixes=('_MPS', '_Borough'))

# Correlation between Trust MPS and other measures
correlation_mps = df_mps_pivot[numeric_columns_mps].corr()
correlation_borough = df_borough_pivot[numeric_columns_borough].corr()

# Scatter plot for visualization
scatter_plot_data = df_mps_pivot.dropna(subset=["Trust MPS"])

selected_measure = st.selectbox('Select Measure', options=["Listen to concerns", "Relied on to be there", "Understand issues"])


# Create layout for scatter plot and multi-axis plot
st.header(f"Scatter plot for Trust MPS vs {selected_measure}", anchor=None)
plot_scatter_with_regression(scatter_plot_data, selected_measure, "Trust MPS", f"Trust MPS vs {selected_measure}")

# Create the multi-axis plot
st.header("Multi-Axis Interactive Plot: Police Responsiveness and Trust MPS", anchor=None)
multi_axis_fig = create_multi_axis_plot(df_mps_pivot)

# Display the plot in Streamlit
st.plotly_chart(multi_axis_fig, use_container_width=True)
