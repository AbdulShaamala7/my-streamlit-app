import pandas as pd
import streamlit as st
import altair as alt

# Load the data
file_path = 'C:/Users/n11500832/OneDrive - Queensland University of Technology/ABE_Project/ABE_Topic.csv'
data = pd.read_csv(file_path, encoding='ISO-8859-1')

# Fix column names if necessary by stripping leading/trailing spaces
data.columns = data.columns.str.strip()

# Set the correct column name for topics
topic_column = 'Topic Cluster'

# Custom CSS for fancy design and distinct column backgrounds
st.markdown(
    """
    <style>
    .main {
        max-width: 1800px;
        margin-left: auto;
        margin-right: auto;
        padding: 20px;
        background-color: #F9F9F9;
    }

    .stApp {
        background: #F0F2F6;
    }

    .sidebar .sidebar-content {
        background-color: #A9CCE3;
        color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
    }

    .sidebar .sidebar-content h2 {
        font-family: 'Arial', sans-serif;
        color: #FFFFFF;
        background-color: #007098;
    }

    .stTextInput, .stSelectbox {
        background-color: #FFFFFF;
        color: #00274d;
        border-radius: 10px;
        font-size: 16px;
    }

    .stDataFrame {
        font-family: 'Arial', sans-serif;
        font-size: 14px;
    }

    h1 {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #004466;
    }

    h2 {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #006699;
    }

    h3 {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #006699;
    }

    .metrics {
        font-size: 15px;
    }

    .altair-chart {
        padding: 10px;
        border-radius: 15px;
        background: white;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
    }
    .right-column h2 {
        color: #004466;
    }

    /* Fancy table style */
    .stTable {
        border-radius: 10px;
        border: 1px solid #ccc;
        background-color: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar content for researcher and topic selection
st.sidebar.title("Options")

# Researcher selection in the sidebar
researchers = [col for col in data.columns if col not in [topic_column] and not col.endswith('.1')]
default_researcher_option = "Select Researcher"
researchers.insert(0, default_researcher_option)
selected_researcher = st.sidebar.selectbox("Select a Researcher:", researchers)

# Topic selection in the sidebar
topics = data[topic_column].dropna().unique()
default_topic_option = "Select Topic"
topics = [default_topic_option] + list(topics)
selected_topic = st.sidebar.selectbox("Select a Topic:", topics)

# Main content
st.title("Researcher Data by Topic")

# Divide the page into two columns for content with custom widths
col1, col2 = st.columns([3, 1])  # Column 1 is wider to accommodate the larger chart

# -------------------------------------------
# Left Column (Researcher-based Analysis)
# -------------------------------------------
if selected_researcher != default_researcher_option:
    with col1:
        st.subheader(f"Data for Researcher: {selected_researcher}")

        # Prepare the data for the chart
        researcher_data = data[[topic_column, selected_researcher, f"{selected_researcher}.1"]].dropna()
        researcher_data.columns = ['Topic', 'Scholarly Output', 'F-WCI']

        # Convert the columns to numeric to avoid string comparison issues
        researcher_data['Scholarly Output'] = pd.to_numeric(researcher_data['Scholarly Output'], errors='coerce').astype(int)
        researcher_data['F-WCI'] = pd.to_numeric(researcher_data['F-WCI'], errors='coerce').round(2)

        # Filter out rows where both 'Scholarly Output' and 'F-WCI' are NaN or 0
        researcher_data = researcher_data[(researcher_data['Scholarly Output'] > 0) | (researcher_data['F-WCI'] > 0)]

        # Melt the data to get it in long format for Altair
        researcher_data_melted = researcher_data.melt('Topic', var_name='Metric', value_name='Value')

        # Get the number of unique topics
        num_topics = researcher_data_melted['Topic'].nunique()

        # Set the space between bars: 70 for fewer than 3 topics, 60 for 7 or fewer topics, and 40 for more than 7 topics
        if num_topics < 3:
            bar_spacing = 120
        elif num_topics <= 10:
            bar_spacing = 60
        else:
            bar_spacing = 40

        # Create a grouped bar chart (each metric has its own bar)
        chart = alt.Chart(researcher_data_melted).mark_bar(size=30).encode(
            y=alt.Y('Topic:N', sort=alt.EncodingSortField(field="Scholarly Output", order="descending"),
                    axis=alt.Axis(title='Topics', labelFontSize=12, labelLimit=500, titlePadding=10,titleAngle=0, titleY=-30)),
            x=alt.X('Value:Q', axis=alt.Axis(title='Value', labelFontSize=12, grid=True),
                    scale=alt.Scale(domain=[0, 35])),  # Fixed scale for Value axis
            color=alt.Color('Metric:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="Metrics")),
            tooltip=['Topic', 'Metric', 'Value']
        ).properties(
            width=900,  # Set width for the chart (adjust this value to make it wider)
            height=num_topics * bar_spacing  # Set height based on number of topics and custom spacing
        )

        # Display the chart in the left column
        st.altair_chart(chart)

# -------------------------------------------
## Right Column (Topic-based Analysis)
if selected_topic != default_topic_option:
    with col2:
        # Start the right column with a custom background and padding
        st.markdown('<div class="right-column">', unsafe_allow_html=True)

        st.subheader(f"Researchers for Topic: {selected_topic}")

        # Filter the researchers who have data for the selected topic
        researcher_columns_scholarly = [col for col in data.columns if col not in [topic_column] and not col.endswith('.1')]
        researcher_columns_f_wci = [col for col in data.columns if col.endswith('.1')]

        # Filter data for the selected topic
        topic_data = data[data[topic_column] == selected_topic]

        # Create a DataFrame for the relevant researchers and metrics
        researchers_data = pd.DataFrame({
            'Researcher': researcher_columns_scholarly,
            'Scholarly Output': topic_data[researcher_columns_scholarly].values[0],
            'F-WCI': topic_data[researcher_columns_f_wci].values[0]
        })

        # Convert 'Scholarly Output' and 'F-WCI' to numeric values, coercing errors to NaN
        researchers_data['Scholarly Output'] = pd.to_numeric(researchers_data['Scholarly Output'], errors='coerce')
        researchers_data['F-WCI'] = pd.to_numeric(researchers_data['F-WCI'], errors='coerce')

        # Remove rows where both 'Scholarly Output' and 'F-WCI' are NaN or 0
        researchers_data = researchers_data[(researchers_data['Scholarly Output'] > 0) | (researchers_data['F-WCI'] > 0)]

        # Format F-WCI values to two decimal places
        researchers_data['F-WCI'] = researchers_data['F-WCI'].map(lambda x: f"{x:.2f}")

        # Sort researchers by Scholarly Output in descending order
        researchers_data = researchers_data.sort_values(by='Scholarly Output', ascending=False)

        # Reset the index and remove the row numbers
        researchers_data = researchers_data[['Researcher', 'Scholarly Output', 'F-WCI']].reset_index(drop=True)

        # Display the table without row numbers
        st.table(researchers_data)

        # End the custom background styling for the right column
        st.markdown('</div>', unsafe_allow_html=True)
