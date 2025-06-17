from fastapi import FastAPI, Query
from typing import Optional
import pandas as pd
from api.conversion_only_culture import create_client_TTC_dataframe
from database_functions import (
    get_database_connection,
)

from sqlalchemy import text
from datetime import datetime

app = FastAPI()

def calculate_conversion(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['conversion'] = df['payment_confirmation_loaded'] / df['traffic']
    return df

@app.get("/realtime/")
def get_realtime(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    culture: str = Query(..., description="Culture code, e.g., 'CL'"),
    device: str = Query(..., description="Device type, e.g., 'desktop' or 'mobile'"),
):
    df = create_client_TTC_dataframe(start_date, end_date, culture, device)
    df = calculate_conversion(df)
    return df.to_dict(orient="records")

@app.get("/historical/")
def get_historical(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    culture: Optional[str] = Query(None, description="Culture code, e.g., 'CL'"),
    device: Optional[str] = Query(None, description="Device type, e.g., 'desktop' or 'mobile'"),
):
    engine = get_database_connection()
    table_name = 'conversion_device_culture'
    query = f"SELECT * FROM {table_name} WHERE date BETWEEN :start_date AND :end_date"
    params = {"start_date": start_date, "end_date": end_date}
    if culture:
        query += " AND culture = :culture"
        params["culture"] = culture
    if device:
        query += " AND device = :device"
        params["device"] = device
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    if df.empty:
        return []
    df = calculate_conversion(df)
    return df.to_dict(orient="records")

@app.get("/health")
def health():
    return {"status": "ok"} 