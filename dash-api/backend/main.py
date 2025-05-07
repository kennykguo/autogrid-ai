# from fastapi import FastAPI, HTTPException, Query
# from typing import List
# from forecasting import predict_solar, predict_wind
# from rl_agent import RLRequest, agent  # import the agent instance directly

# app = FastAPI(title="Microgrid API")


# @app.get("/forecast/solar")
# async def forecast_solar(
#     features: List[float] = Query(..., description="e.g. ?features=1.2&features=3.4&…")
# ):
#     try:
#         prediction = predict_solar(features)
#         return {"model": "solar", "prediction": prediction}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.get("/forecast/wind")
# async def forecast_wind(
#     features: List[float] = Query(..., description="e.g. ?features=5.6&features=7.8&…")
# ):
#     try:
#         prediction = predict_wind(features)
#         return {"model": "wind", "prediction": prediction}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/rl/action")
# async def rl_action(request: RLRequest):
#     try:
#         action = agent.act(request.state)
#         return {"action": action}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from forecasting import (
    predict_solar,
    predict_wind,
    predict_non_critical_load,
    predict_critical_load,
    predict_essential_load,
)
from rl_agent import RLRequest, agent

app = FastAPI(title="Microgrid API")

class ForecastRequest(BaseModel):
    features: List[List[float]]  # window_size × input_dim

@app.post("/forecast/solar")
async def forecast_solar(req: ForecastRequest):
    try:
        return {"model": "solar", "prediction": predict_solar(req.features)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/forecast/wind")
async def forecast_wind(req: ForecastRequest):
    try:
        return {"model": "wind", "prediction": predict_wind(req.features)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/forecast/non_critical_load")
async def forecast_non_critical_load(req: ForecastRequest):
    try:
        return {"model": "non_critical_load", "prediction": predict_non_critical_load(req.features)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/forecast/critical_load")
async def forecast_critical_load(req: ForecastRequest):
    try:
        return {"model": "critical_load", "prediction": predict_critical_load(req.features)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/forecast/essential_load")
async def forecast_essential_load(req: ForecastRequest):
    try:
        return {"model": "essential_load", "prediction": predict_essential_load(req.features)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/rl/action")
async def rl_action(req: RLRequest):
    try:
        return {"action": agent.act(req.state)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
