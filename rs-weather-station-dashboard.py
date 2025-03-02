import supabase
# from st_supabase_connection import SupabaseConnection
from supabase import create_client
import json
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import time
import datetime
import streamlit as st
import plost
import gspread
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from gspread_pandas import Spread, Client
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from PIL import Image
import json
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Create Supabase client
supabase: Client = create_client(API_URL, API_KEY)

st.set_page_config(
    page_title="Fresco Lapasan Weather Station",
    layout='wide'
)

st.title("Fresco Weather Station")

# Fetch data from both tables
weather_data = supabase.table('fresco-weather-data').select('*').execute()
light_data = supabase.table('fresco-light-uv-data').select('*').execute()

weather_df = pd.DataFrame(weather_data.data)
light_df = pd.DataFrame(light_data.data)

# Date picker setup
datePicker, startDate, endDate, refreshData = st.columns(4)

with datePicker:
    today = datetime.date.today()
    min_date = today
    max_date = today + datetime.timedelta(days=1)
    a_date = st.date_input("Pick a date", (min_date, max_date))

date_start_str = a_date[0].strftime("%B %d, %Y")
date_end_str = a_date[-1].strftime("%B %d, %Y")

with startDate:
    st.write(f"Start: {date_start_str}")

with endDate:
    st.write(f"End: {date_end_str}")

with refreshData:
    if st.button('Refresh Data'):
        st.rerun()

# Convert timestamps
def convert_timestamp(timestamp):
    datetime_obj = pd.to_datetime(timestamp)
    return (datetime_obj + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

# Process weather data
weather_df['created_at'] = weather_df['created_at'].apply(convert_timestamp)
weather_df['created_at'] = pd.to_datetime(weather_df['created_at'])

# Process light data
light_df['created_at'] = light_df['created_at'].apply(convert_timestamp)
light_df['created_at'] = pd.to_datetime(light_df['created_at'])

# Filter data by date range
date_start = pd.Timestamp(a_date[0])
date_end = pd.Timestamp(a_date[-1])

weather_df = weather_df[(weather_df['created_at'] >= date_start) & (weather_df['created_at'] <= date_end)]
light_df = light_df[(light_df['created_at'] >= date_start) & (light_df['created_at'] <= date_end)]

# Divide values that were multiplied by 100
weather_df['windSpeed_out_a'] = weather_df['windSpeed_out_a'] / 100
weather_df['temp_out_a'] = weather_df['temp_out_a'] / 100
weather_df['hum_out_a'] = weather_df['hum_out_a'] / 100
weather_df['altitude_a'] = weather_df['altitude_a'] / 100
weather_df['press_out_a'] = weather_df['press_out_a'] / 100
weather_df['co2_out_a'] = weather_df['co2_out_a'] / 100

# Filter out humidity outliers (values above 100)
weather_df = weather_df[weather_df['hum_out_a'] <= 100]  # Add this line to filter humidity outliers

# Create dashboard layout
weather1, weather2 = st.columns(2)

with weather1:
    st.markdown("## Temperature (°C)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['temp_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with weather2:
    st.markdown("## Humidity (%)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['hum_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

weather3, weather4 = st.columns(2)

with weather3:
    st.markdown("## Wind Speed (m/s)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['windSpeed_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with weather4:
    st.markdown("## Wind Direction")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['windDir_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

weather5, weather6 = st.columns(2)

with weather5:
    st.markdown("## Pressure (hPa)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['press_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with weather6:
    st.markdown("## Altitude (m)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['altitude_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

air_quality1, air_quality2, air_quality3 = st.columns(3)

with air_quality1:
    st.markdown("## CO2 (ppm)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['co2_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with air_quality2:
    st.markdown("## TVOC (ppb)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['tvoc_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with air_quality3:
    st.markdown("## H2")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weather_df['created_at'], y=weather_df['h2_out_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

light1, light2 = st.columns(2)

with light1:
    st.markdown("## UV Index")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=light_df['created_at'], y=light_df['uv_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

with light2:
    st.markdown("## Light Intensity (lux)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=light_df['created_at'], y=light_df['lux_a'], mode='lines'))
    fig.update_layout(xaxis_rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# Display raw data tables
st.subheader('Weather Station Data')
st.dataframe(weather_df, use_container_width=True)

st.subheader('Light/UV Sensor Data')
st.dataframe(light_df, use_container_width=True)


