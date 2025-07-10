import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

# Streamlit config
st.set_page_config(page_title="EV Dashboard", layout="wide")

st.title("⚡ EV Data Dashboard – India")
st.markdown("""
This interactive dashboard shows electric vehicle (EV) registration trends across India.

*Filters:* Choose any combination of states and years to explore the data.
""")

# Load data
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv("EV_Dataset.csv")
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame({
            'Year': np.random.choice([2018, 2019, 2020, 2021, 2022], 100),
            'State': np.random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat'], 100),
            'Vehicle_Class': np.random.choice(['Sedan', 'SUV', 'Hatchback', 'Truck', 'Van'], 100)
        })

df = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filter Data")

if df.empty:
    st.warning("No data available to display.")
    st.stop()

try:
    state_options = sorted(df['State'].dropna().unique())
    year_options = sorted(df['Year'].dropna().unique().astype(int))
except Exception as e:
    st.error(f"Error processing data: {e}")
    state_options = []
    year_options = []

default_states = state_options[:3] if len(state_options) >= 3 else state_options
default_years = year_options if year_options else []

selected_states = st.sidebar.multiselect("Select States", state_options, default=default_states)
selected_years = st.sidebar.multiselect("Select Years", year_options, default=default_years)

# Filter data
if selected_states and selected_years:
    filtered_df = df[(df['State'].isin(selected_states)) & (df['Year'].isin(selected_years))]
elif selected_states:
    filtered_df = df[df['State'].isin(selected_states)]
elif selected_years:
    filtered_df = df[df['Year'].isin(selected_years)]
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # ========= FIRST ROW ==========
    col1, col2 = st.columns(2)

    # EV Registrations by Year
    with col1:
        st.subheader("📅 EV Registrations by Year")
        try:
            ev_by_year = df['Year'].value_counts().sort_index()
            fig1, ax1 = plt.subplots(figsize=(7, 4))  # Equal size
            sns.barplot(x=ev_by_year.index.astype(str), y=ev_by_year.values, palette="viridis", ax=ax1)
            ax1.set_title("Total EVs by Year", fontsize=12)
            ax1.set_xlabel("Year", fontsize=10)
            ax1.set_ylabel("Registrations", fontsize=10)
            plt.xticks(rotation=45)  # ROTATE X-AXIS LABELS
            for i, v in enumerate(ev_by_year.values):
                ax1.text(i, v + (v * 0.02), f"{v:,}", ha='center', fontsize=8)
            ax1.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig1)
        except Exception as e:
            st.error(f"Error creating year chart: {e}")

    # EV Registrations by State
    with col2:
        st.subheader("🌍 EV Registrations by State")
        try:
            state_counts = filtered_df['State'].value_counts()
            if not state_counts.empty:
                fig2, ax2 = plt.subplots(figsize=(7, 4))  # Same size
                sns.barplot(x=state_counts.index, y=state_counts.values, palette="Greens", ax=ax2)
                ax2.set_xlabel("State", fontsize=10)
                ax2.set_ylabel("Registrations", fontsize=10)
                ax2.set_title("EVs by State", fontsize=12)
                plt.xticks(rotation=45)  # ROTATE X-AXIS LABELS
                for i, v in enumerate(state_counts.values):
                    ax2.text(i, v + (v * 0.02), f"{v:,}", ha='center', fontsize=8)
                ax2.grid(axis='y', linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig2)
            else:
                st.info("No state data available for the selected filters.")
        except Exception as e:
            st.error(f"Error creating state chart: {e}")

    # ========= SECOND ROW ==========
    col3, col4 = st.columns(2)

    # Vehicle Class Pie Chart
    with col3:
        st.subheader("🚗 Vehicle Class Distribution")
        if 'Vehicle_Class' in filtered_df.columns:
            try:
                vehicle_counts = filtered_df['Vehicle_Class'].value_counts()
                if not vehicle_counts.empty:
                    if len(vehicle_counts) > 6:
                        top_classes = vehicle_counts.iloc[:6]
                        others = pd.Series({'Others': vehicle_counts.iloc[6:].sum()})
                        vehicle_counts = pd.concat([top_classes, others])

                    fig3 = px.pie(
                        values=vehicle_counts.values,
                        names=vehicle_counts.index,
                        title="Vehicle Class Distribution",
                        color_discrete_sequence=px.colors.sequential.Blues,
                        hover_data=[vehicle_counts.values]
                    )
                    fig3.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>Count: %{customdata[0]}<br>Percentage: %{percent}'
                    )
                    fig3.update_layout(
                        width=500,
                        height=350,
                        title_font_size=14,
                        margin=dict(t=40, b=30),
                        showlegend=False
                    )
                    st.plotly_chart(fig3, use_container_width=False)
                else:
                    st.info("No vehicle class data available for the selected filters.")
            except Exception as e:
                st.error(f"Error creating vehicle class chart: {e}")
        else:
            st.warning("Vehicle_Class column not found in the data.")

    # Line Chart for One State
    with col4:
        st.subheader("📈 EV Registration Trend in One State")
        try:
            available_states = sorted(df['State'].dropna().unique())
            if available_states:
                selected_single_state = st.selectbox("Select a State for Line Chart", available_states)
                state_df = df[df['State'] == selected_single_state]

                if not state_df.empty:
                    state_yearly = state_df['Year'].value_counts().sort_index()
                    fig4, ax4 = plt.subplots(figsize=(7, 4))  # Same size
                    sns.lineplot(x=state_yearly.index.astype(str), y=state_yearly.values, marker='o', ax=ax4)
                    ax4.set_title(f"EV Registrations in {selected_single_state}", fontsize=12)
                    ax4.set_xlabel("Year", fontsize=10)
                    ax4.set_ylabel("Registrations", fontsize=10)
                    plt.xticks(rotation=45)  # ROTATE X-AXIS LABELS
                    ax4.grid(True, alpha=0.5)
                    plt.tight_layout()
                    st.pyplot(fig4)
                else:
                    st.info(f"No data available for {selected_single_state}.")
            else:
                st.info("No states available in the dataset.")
        except Exception as e:
            st.error(f"Error creating line chart: {e}")

# Footer
st.markdown("---")
st.markdown("**Data Source:** Electric Vehicle Registration Dataset")
