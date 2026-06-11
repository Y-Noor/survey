import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Survey Dashboard", layout="wide")
st.title("📊 Survey Results Dashboard")

# 1. Connect to Google Sheets
# (Make sure to set up secrets for this, see Step 3)
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data (adjust 'worksheet' to your specific tab name if needed)
df = conn.read(ttl="10m")  # Caches data for 10 minutes

st.subheader("Raw Survey Data")
st.dataframe(df.head())

# --- Basic Data Cleansing / Validation Example ---
# Ensure your column names match your sheet exactly. 
# Let's assume you have columns: 'Age Group', 'Satisfaction', 'Feature Request'

# 2. Add Sidebar Filters
st.sidebar.header("Filter Results")
if 'Age Group' in df.columns:
    age_filter = st.sidebar.multiselect(
        "Select Age Group:",
        options=df['Age Group'].unique(),
        default=df['Age Group'].unique()
    )
    df_filtered = df[df['Age Group'].isin(age_filter)]
else:
    df_filtered = df

# 3. Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Satisfaction Ratings")
    if 'Satisfaction' in df_filtered.columns:
        # Count occurrences of each rating
        satisfaction_counts = df_filtered['Satisfaction'].value_counts().reset_index()
        satisfaction_counts.columns = ['Rating', 'Count']
        
        # Create a Bar Chart
        fig_bar = px.bar(satisfaction_counts, x='Rating', y='Count', 
                         color='Rating', title="Overall Satisfaction Distribution")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Add a 'Satisfaction' column to see this chart.")

with col2:
    st.subheader("Demographics Breakdown")
    if 'Age Group' in df_filtered.columns:
        # Create a Pie Chart
        fig_pie = px.pie(df_filtered, names='Age Group', title="Respondents by Age Group")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Add an 'Age Group' column to see this chart.")

# 4. Text/Open-ended Survey Responses
st.subheader("💬 Open-ended Feedback")
if 'Feature Request' in df_filtered.columns:
    for i, response in enumerate(df_filtered['Feature Request'].dropna()):
        st.markdown(f"**Respondent {i+1}:** {response}")