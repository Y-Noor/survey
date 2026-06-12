import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Survey Dashboard", layout="wide")
st.title("Survey Results Dashboard")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data
df = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/1Nsodfc0cmxsohQ43jN-m2KWsPonGkZJRmC-ArC1HN5I/edit?usp=sharing",
    ttl="10m"
)

# Clean data slightly (drop completely empty rows/columns if any)
df = df.dropna(how='all')

# Display Data Overview
st.subheader("Respondent Data Overview")
st.dataframe(df.head(), use_container_width=True)
st.markdown("---")

# ------------------------------------------------------------------
# NEW SECTION: Total Representation Count Across All Questions
# ------------------------------------------------------------------
st.subheader("Total Responses Across All Questions")

# Identify columns to ignore for the global count (like timestamps or IDs)
ignore_cols = ['id', 'timestamp', 'index']
valid_cols = [col for col in df.columns if col.lower() not in ignore_cols]

if valid_cols:
    # Melt the dataframe to combine all answers from all columns into one single column
    melted_df = pd.melt(df, value_vars=valid_cols, value_name='Answer')
    
    # Drop missing values and count occurrences of each unique answer/name
    total_counts = melted_df['Answer'].dropna().value_counts().reset_index()
    total_counts.columns = ['Answer', 'Total Count']
    
    # Sort so the highest represented name is at the top of the chart
    total_counts = total_counts.sort_values(by='Total Count', ascending=True)
    
    if not total_counts.empty:
        # Create a horizontal bar chart (clean and easy to read for names)
        fig_total = px.bar(
            total_counts, 
            x='Total Count', 
            y='Answer', 
            orientation='h',
            title="Total Frequency of Each Answer Across Entire Survey",
            color='Total Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        
        fig_total.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=min(400 + (len(total_counts) * 20), 800) # Dynamic height based on number of names
        )
        
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.info("No valid answers found to aggregate.")
else:
    st.info("No valid survey question columns found.")

st.markdown("---")

# ------------------------------------------------------------------
# VISUAL CARDS: Question-by-Question Breakdown
# ------------------------------------------------------------------
st.subheader("Question-by-Question Breakdown")

CARDS_PER_ROW = 2 
columns_to_plot = df.columns

for i in range(0, len(columns_to_plot), CARDS_PER_ROW):
    cols = st.columns(CARDS_PER_ROW)
    
    for j in range(CARDS_PER_ROW):
        if i + j < len(columns_to_plot):
            question_name = columns_to_plot[i + j]
            
            if question_name.lower() in ignore_cols:
                continue
                
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"### {question_name}")
                    
                    data_counts = df[question_name].value_counts().reset_index()
                    data_counts.columns = ['Response', 'Count']
                    
                    if not data_counts.empty:
                        fig = px.pie(
                            data_counts, 
                            names='Response', 
                            values='Count',
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=20, b=20),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No data submitted for this question yet.")