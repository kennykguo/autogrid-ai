from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from load_model import load_agent
import numpy as np
from typing import Dict
from datetime import datetime, timedelta
import traceback
import aiohttp
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
last_prediction = None
last_prediction_time = None
last_weather_data = None
last_weather_time = None

async def fetch_norway_weather(lat=59.9139, lon=10.7522):
    """Fetch weather data from Met Norway API"""
    global last_weather_data, last_weather_time
    
    # Return cached weather if less than 30 minutes old
    now = datetime.now()
    if last_weather_data and last_weather_time:
        if (now - last_weather_time).total_seconds() < 1800:
            return last_weather_data
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}",
                headers={"User-Agent": "AutoGridAI/1.0 (https://autogrid.ai)"}
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Weather API request failed")
                data = await response.json()
                
                # Cache the weather data
                last_weather_data = data
                last_weather_time = now
                return data
    except Exception as e:
        print(f"Error fetching weather: {str(e)}")
        if last_weather_data:
            return last_weather_data
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

def get_model():
    """Get or initialize the PPO model."""
    global model
    if model is None:
        try:
            model = load_agent()
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    return model

def get_state_observation(weather_data):
    """Create observation vector for the model including weather data."""
    # Time of day normalized to [0,1]
    current_hour = datetime.now().hour
    time_of_day = current_hour / 24.0
    
    # Get current weather metrics from the first timepoint
    try:
        current = weather_data["properties"]["timeseries"][0]["data"]["instant"]["details"]
        temperature = current.get("air_temperature", 20) / 40.0  # Normalize to [0,1]
        wind_speed = current.get("wind_speed", 0) / 20.0  # Normalize to [0,1]
        cloud_cover = current.get("cloud_area_fraction", 50) / 100.0  # Already [0,1]
    except (KeyError, IndexError):
        temperature, wind_speed, cloud_cover = 0.5, 0.5, 0.5
    
    # Create a 32-dimensional observation vector
    observation = np.zeros(32)
    
    # Core features (0-7)
    observation[0] = time_of_day
    observation[1] = 0.5  # Battery state of charge [0,1]
    observation[2] = (1 - cloud_cover) * 0.8  # Solar potential based on cloud cover
    observation[3] = wind_speed  # Wind potential
    observation[4] = 0.8  # Grid availability [0,1]
    observation[5] = 0.6  # Demand forecast [0,1]
    observation[6] = temperature  # Temperature (normalized)
    observation[7] = cloud_cover  # Cloud cover [0,1]
    
    # Historical values (8-15)
    observation[8:16] = observation[0:8] * 0.9
    
    # Future predictions from weather forecast (16-23)
    try:
        future = weather_data["properties"]["timeseries"][4]["data"]["instant"]["details"]
        future_temp = future.get("air_temperature", 20) / 40.0
        future_wind = future.get("wind_speed", 0) / 20.0
        future_cloud = future.get("cloud_area_fraction", 50) / 100.0
        
        observation[16] = time_of_day
        observation[17] = 0.5  # Future battery prediction
        observation[18] = (1 - future_cloud) * 0.8
        observation[19] = future_wind
        observation[20] = 0.8  # Future grid availability
        observation[21] = 0.6  # Future demand prediction
        observation[22] = future_temp
        observation[23] = future_cloud
    except (KeyError, IndexError):
        observation[16:24] = observation[0:8] * 1.1
    
    # Moving averages and additional features (24-31)
    observation[24:32] = (observation[0:8] + observation[8:16] + observation[16:24]) / 3
    
    return observation.astype(np.float32)

@app.get("/predict")
async def predict_actions() -> Dict:
    global last_prediction, last_prediction_time
    
    try:
        current_time = datetime.now()
        
        # Check if we have a valid prediction for the current hour
        if (last_prediction is not None and last_prediction_time is not None and
            last_prediction_time.hour == current_time.hour):
            return last_prediction
            
        # Get next hour for prediction period
        next_hour = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        # Get weather data
        weather_data = await fetch_norway_weather()
        
        # Get the model
        model = get_model()
        
        # Get observation state including weather
        observation = get_state_observation(weather_data)
        
        # Get model prediction
        action, _states = model.predict(observation, deterministic=True)
        
        # Scale actions based on weather conditions
        current_weather = weather_data["properties"]["timeseries"][0]["data"]["instant"]["details"]
        cloud_cover = current_weather.get("cloud_area_fraction", 50) / 100.0
        wind_speed = current_weather.get("wind_speed", 0)
        
        # Adjust solar and wind based on weather
        solar_factor = max(0.2, 1 - cloud_cover)
        wind_factor = min(1.0, wind_speed / 10.0)
        
        prediction = {
            "currentTimestamp": current_time.isoformat(),
            "predictionPeriod": next_hour.isoformat(),
            "solarOutput": float(max(0, action[0] * 10 * solar_factor)),
            "windOutput": float(max(0, action[1] * 8 * wind_factor)),
            "batteryCharge": float(max(0, min(100, 50 + action[2] * 50))),
            "houseConsumption": float(max(0, 5 + action[3] * 3)),
            "gridConnection": float(action[4] * 15)
        }
        
        # Cache the prediction
        last_prediction = prediction
        last_prediction_time = current_time
        
        return prediction
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    try:
        model = get_model()
        return {"status": "healthy", "model_loaded": model is not None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
