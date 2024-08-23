import os
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
import requests
import json

app = FastAPI()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "RnGEjPoMpDNZC2igxQRttmZsOYCHkQNI")
POLYGON_API_URL = "https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start}/{end}"

# Get Redis connection details from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "admin")  # Ensure this matches your redis.conf

# Initialize Redis client with password
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)

CACHE_EXPIRATION = 3600  # 1 hour

def refresh_cache(ticker: str, multiplier: int, timespan: str, start_date: str, end_date: str):
    cache_key = f"{ticker}_{multiplier}_{timespan}_{start_date}_{end_date}"
    url = POLYGON_API_URL.format(ticker=ticker, multiplier=multiplier, timespan=timespan, start=start_date, end=end_date)
    response = requests.get(url, params={"apiKey": POLYGON_API_KEY})
    if response.status_code == 200:
        redis_client.set(cache_key, response.text, ex=CACHE_EXPIRATION)

@app.get("/historical-data/")
def get_historical_data(ticker: str, multiplier: int, timespan: str, start_date: str, end_date: str, background_tasks: BackgroundTasks):
    cache_key = f"{ticker}_{multiplier}_{timespan}_{start_date}_{end_date}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        # Trigger background cache refresh
        background_tasks.add_task(refresh_cache, ticker, multiplier, timespan, start_date, end_date)
        return json.loads(cached_data)

    # If data is not in cache, request from Polygon.io
    url = POLYGON_API_URL.format(ticker=ticker, multiplier=multiplier, timespan=timespan, start=start_date, end=end_date)
    response = requests.get(url, params={"apiKey": POLYGON_API_KEY})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Store response in Redis cache
    redis_client.set(cache_key, response.text, ex=CACHE_EXPIRATION)
    return response.json()
