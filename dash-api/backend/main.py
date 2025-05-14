import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from fastapi import FastAPI, HTTPException
import uvicorn
from stable_baselines3 import PPO
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Microgrid API")

# allow your Next dev server to call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─── Transformer definition & loading ───────────────────────────────────────────
class TimeSeriesTransformer(nn.Module):
    WINDOW_SIZE        = 10
    TRANSFORMER_DIM    = 64
    TRANSFORMER_HEADS  = 4
    TRANSFORMER_LAYERS = 2
    DROPOUT_RATE       = 0.1

    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.encoder = nn.Linear(input_dim, self.TRANSFORMER_DIM)
        self.pos_encoder = nn.Parameter(torch.zeros(self.WINDOW_SIZE, self.TRANSFORMER_DIM))
        layer = nn.TransformerEncoderLayer(
            d_model=self.TRANSFORMER_DIM,
            nhead=self.TRANSFORMER_HEADS,
            dropout=self.DROPOUT_RATE,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(layer, num_layers=self.TRANSFORMER_LAYERS)
        self.decoder = nn.Linear(self.TRANSFORMER_DIM, output_dim)

    def forward(self, x):
        x = self.encoder(x)
        x = x + self.pos_encoder.unsqueeze(0)
        x = self.transformer_encoder(x)
        return self.decoder(x[:, -1, :])

MODEL_DIR = Path(__file__).parent / "models"

def _load_model(fname: str) -> nn.Module:
    ckpt = torch.load(MODEL_DIR / fname, map_location="cpu")
    if isinstance(ckpt, dict):
        in_d = ckpt["encoder.weight"].size(1)
        out_d = ckpt["decoder.weight"].size(0)
        m = TimeSeriesTransformer(in_d, out_d)
        m.load_state_dict(ckpt)
        return m.eval()
    else:
        return ckpt.eval()

solar_model      = _load_model("solar_model.pt")
wind_model       = _load_model("wind_model.pt")
noncrit_model    = _load_model("non_critical_load_model.pt")
crit_model       = _load_model("critical_load_model.pt")
essential_model  = _load_model("essential_load_model.pt")

def predict_solar(f):      return float(solar_model(torch.tensor(f, dtype=torch.float32)).squeeze().item())
def predict_wind(f):       return float(wind_model(torch.tensor(f, dtype=torch.float32)).squeeze().item())
def predict_noncrit(f):    return float(noncrit_model(torch.tensor(f, dtype=torch.float32)).squeeze().item())
def predict_crit(f):       return float(crit_model(torch.tensor(f, dtype=torch.float32)).squeeze().item())
def predict_essential(f):  return float(essential_model(torch.tensor(f, dtype=torch.float32)).squeeze().item())

# ─── Forecast one-step ─────────────────────────────────────────────────────────
def run_forecast_one(df: pd.DataFrame, scalermap: dict) -> pd.DataFrame:
    model_map = {
        'Solar_Pred':       solar_model,
        'Wind_Pred':        wind_model,
        'Non_Critical_Pred': noncrit_model,
        'Critical_Pred':    crit_model,
        'Essential_Pred':   essential_model
    }
    model_features = {
        'Solar_Pred': [
            'PVPCS_Active_Power',
            'Temperature',
            'hour',
            'day',
            'month',
            'day_of_week',
            'is_weekend'
        ],
        'Wind_Pred': [
            'Wind_Power',
            'Wind_Speed',
            'hour',
            'day',
            'month',
            'day_of_week',
            'is_weekend'
        ],
        'Non_Critical_Pred': [
            'Non_Critical_Power_Load',
            'hour',
            'day',
            'month',
            'day_of_week',
            'is_weekend'
        ],
        'Critical_Pred': [
            'Critical_Power_Load',
            'hour',
            'day',
            'month',
            'day_of_week',
            'is_weekend'
        ],
        'Essential_Pred': [
            'Essential_Power_Load',
            'hour',
            'day',
            'month',
            'day_of_week',
            'is_weekend'
        ]
    }

    last_time = df.index[-1]
    results = {}

    for name in model_map:
        features = df[model_features[name]].values
        if name == 'Solar_Pred':
            y_s = predict_solar(features)
        elif name == 'Wind_Pred':
            y_s = predict_wind(features)
        elif name == 'Non_Critical_Pred':
            y_s = predict_noncrit(features)
        elif name == 'Critical_Pred':
            y_s = predict_crit(features)
        else:
            y_s = predict_essential(features)

        inv = scalermap[name].inverse_transform([[y_s]])[0, 0]
        results[name] = inv

    ts = last_time + pd.Timedelta(hours=1)
    out = pd.DataFrame(results, index=[ts])
    out.index.name = 'Timestamp'
    return out.reset_index()

# ─── RL agent ─────────────────────────────────────────────────────────────────
class RLAgent:
    def __init__(self, path: str):
        self.model = PPO.load(path, verbose=0)

    def act(self, state: List[float]):
        obs = np.array(state, dtype=np.float32).reshape(1, -1)
        action, _ = self.model.predict(obs, deterministic=True)
        a = np.array(action)[0]
        return a.item() if np.isscalar(a) else a.tolist()

agent = RLAgent(str(MODEL_DIR / "ppo_refined_iteration_3_2025-04-15_16-29-13.zip"))

# ─── FastAPI app ─────────────────────────────────────────────────────────────
CSV = Path(__file__).parent / "merged.csv"
app = FastAPI(title="Microgrid API")

@app.get("/forecast/next", response_model=Dict[str, Any])
def forecast_next():
    try:
        df = pd.read_csv(CSV)
        df.index = pd.date_range(start="2023-01-01", periods=len(df), freq="5T")

        WINDOW_SIZE = 10
        scaler_map = {
            'Solar_Pred':        MinMaxScaler().fit(df[['PVPCS_Active_Power']]),
            'Wind_Pred':         MinMaxScaler().fit(df[['Wind_Power']]),
            'Non_Critical_Pred': MinMaxScaler().fit(df[['Non_Critical_Power_Load']]),
            'Critical_Pred':     MinMaxScaler().fit(df[['Critical_Power_Load']]),
            'Essential_Pred':    MinMaxScaler().fit(df[['Essential_Power_Load']])
        }

        df['hour']        = df.index.hour / 23.0
        df['day']         = df.index.day / 31.0
        df['month']       = df.index.month / 12.0
        df['day_of_week'] = df.index.dayofweek / 6.0
        df['is_weekend']  = (df.index.dayofweek >= 5).astype(int)

        df['PVPCS_Active_Power']     = scaler_map['Solar_Pred'].transform(df[['PVPCS_Active_Power']])
        df['Wind_Power']             = scaler_map['Wind_Pred'].transform(df[['Wind_Power']])
        df['Non_Critical_Power_Load'] = scaler_map['Non_Critical_Pred'].transform(df[['Non_Critical_Power_Load']])
        df['Critical_Power_Load']     = scaler_map['Critical_Pred'].transform(df[['Critical_Power_Load']])
        df['Essential_Power_Load']    = scaler_map['Essential_Pred'].transform(df[['Essential_Power_Load']])

        window_df  = df.iloc[-WINDOW_SIZE:].copy()
        prediction = run_forecast_one(window_df, scaler_map)
        print(f"Processed latest window with prediction:\n{prediction}")

        return prediction.to_dict(orient="records")[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rl/action", response_model=Dict[str, Any])
def rl_action():
    try:
        # 1. grab the latest forecast
        forecast = forecast_next()

        # 2. build the 5-dim state vector
        state = [
            forecast["Solar_Pred"],
            forecast["Wind_Pred"],
            forecast["Non_Critical_Pred"],
            forecast["Critical_Pred"],
            forecast["Essential_Pred"],
        ]

        # 3. pad/truncate to match obs-space (32)
        obs_dim = agent.model.observation_space.shape[0]
        if len(state) < obs_dim:
            state += [0.0] * (obs_dim - len(state))
        else:
            state = state[:obs_dim]

        # 4. get the RL action
        action = agent.act(state)

        # 5. return both forecast and action
        return {
            "forecast": forecast,
            "action": action,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
