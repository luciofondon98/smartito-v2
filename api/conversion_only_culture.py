import json
import requests
import pandas as pd
import warnings
from requests.auth import HTTPBasicAuth
import time
import numpy as np
from dotenv import load_dotenv
import os
import datetime

warnings.filterwarnings('ignore')

# Módulos de filtros
from amplitude_filters import (
    get_filters_culture_device
)

from amplitude_events import (
    get_TTC_client_journey
)

load_dotenv()
api_key = os.getenv('AMPLITUDE_API_KEY')
secret_key = os.getenv('AMPLITUDE_SECRET_KEY')


def create_client_TTC_dataframe(start_date, end_date, culture):
    """
    Crea un DataFrame con los datos diarios del funnel entre dos steps
    """
    step_data = get_TTC_client_journey(api_key, secret_key, start_date, end_date, culture)
    step_data = step_data['data'][0]

    # Extraer datos diarios
    daily_data = step_data['dayFunnels']
    dates = daily_data['xValues']
    daily_series = daily_data['series']

    # Crear lista para almacenar los datos diarios
    daily_rows = []

    for i, date in enumerate(dates):
        users_per_step = daily_series[i]
        row_data = {
            'date': date,
            'culture': culture,
            'traffic': users_per_step[0],
            'flight_dom_loaded_flight': users_per_step[1],
            'payment_confirmation_loaded': users_per_step[2],
        }
        daily_rows.append(row_data)

    df = pd.DataFrame(daily_rows)
    df['date'] = pd.to_datetime(df['date'])
    columns_order = [
        'date',
        'culture',
        'traffic',
        'flight_dom_loaded_flight',
        'payment_confirmation_loaded',
    ]
    df = df[columns_order]
    return df


def final_pipeline_client_journey(start_date, end_date):
    start_time = time.time()
    df_final = pd.DataFrame()
    filters = get_filters_culture_device()

    
    for filter in filters:
        culture = filter[0]
        print(culture)
        df_temp = create_client_TTC_dataframe(
            start_date,
            end_date,
            culture,
        )
        df_final = pd.concat([df_final, df_temp], axis=0)

    end_time = time.time()
    print(end_time - start_time)
    return df_final


def generate_monthly_date_ranges(start_year, start_month):
    current_date = datetime.date(start_year, start_month, 1)
    end_date = datetime.date.today()
    while current_date < end_date:
        next_month = current_date.replace(day=28) + datetime.timedelta(days=4)
        next_month = next_month.replace(day=1)
        yield current_date, next_month - datetime.timedelta(days=1)
        current_date = next_month


from database_functions import (
    get_database_connection,
    get_last_update_date,
    check_existing_dates,
    delete_existing_dates,
    insert_data_to_database
)

# Modify the main block to include database operations
if __name__ == "__main__":
    # Create database connection
    engine = get_database_connection()
    table_name = 'conversion_device_culture'

    # Get the last update date from the database
    last_update = get_last_update_date(engine, table_name)
    
    # If table doesn't exist or is empty, start from January 2025
    if not last_update:
        start_year = 2025
        start_month = 1
    else:
        # If table exists, start from the last date
        start_year = last_update.year
        start_month = last_update.month

    # Generate monthly date ranges
    for start_date, end_date in generate_monthly_date_ranges(start_year, start_month):
        print(f"Processing data from {start_date} to {end_date}")
        
        # Check if data already exists for this date range
        if check_existing_dates(engine, table_name, start_date, end_date):
            print(f"Data already exists for {start_date} to {end_date}. Deleting existing records...")
            delete_existing_dates(engine, table_name, start_date, end_date)
        
        # Get data for this date range
        df = final_pipeline_client_journey(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if not df.empty:
            # Insert data into database
            insert_data_to_database(engine, df, table_name)
            print(f"Successfully processed data from {start_date} to {end_date}")
        else:
            print(f"No data available for {start_date} to {end_date}")
