import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Survey Dashboard", layout="wide")
st.title("📊 Survey Results Dashboard")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data (Using the explicit spreadsheet URL approach that worked for you)
df = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/1Nsodfc0cmxsohQ43jN-m2KWsPonGkZJRmC-ArC1HN5I/edit?usp=sharing",
    ttl="10m"
)

# --- Clean data slightly (drop completely empty rows/columns if any) ---
df = df.dropna(how='all')

st.subheader("📋 Respondent Data Overview")
st.dataframe(df.head(), use_container_width=True)
st.markdown("---")

st.subheader("💡 Question-by-Question Breakdown")

# We want a grid layout (e.g., 2 cards per row)
# You can change this to 3 if you want smaller cards
CARDS_PER_ROW = 2 

# Loop through all columns in your Google Sheet dynamically
columns_to_plot = df.columns

for i in range(0, len(columns_to_plot), CARDS_PER_ROW):
    # Create a row of columns based on our CARDS_PER_ROW setting
    cols = st.columns(CARDS_PER_ROW)
    
    for j in range(CARDS_PER_ROW):
        # Ensure we don't go out of bounds if there's an odd number of questions
        if i + j < len(columns_to_plot):
            question_name = columns_to_plot[i + j]
            
            # Skip ID, Timestamp, or purely unique text columns if they ruin the charts
            if question_name.lower() in ['id', 'timestamp', 'index']:
                continue
                
            # Create a visual "Card" using a bordered container
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"### ❓ {question_name}")
                    
                    # Get value counts for the pie chart
                    data_counts = df[question_name].value_counts().reset_index()
                    data_counts.columns = ['Response', 'Count']
                    
                    if not data_counts.empty:
                        # Generate the Pie Chart
                        fig = px.pie(
                            data_counts, 
                            names='Response', 
                            values='Count',
                            hole=0.4, # Turns it into a sleek donut chart! Remove this line for a solid pie
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        
                        # Clean up chart layout inside the card
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=20, b=20),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No data submitted for this question yet.")