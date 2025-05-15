import numpy as np
import pandas as pd
import torch
from typing import List
from pathlib import Path
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

# ─── Model definition ─────────────────────────────────────────────────────────
class TimeSeriesTransformer(nn.Module):
    WINDOW_SIZE        = 10
    TRANSFORMER_DIM    = 64
    TRANSFORMER_HEADS  = 4
    TRANSFORMER_LAYERS = 2
    DROPOUT_RATE       = 0.1

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        d_model: int     = None,
        nhead: int       = None,
        num_layers: int  = None,
        dropout: float   = None,
        window_size: int = None,
    ):
        super().__init__()
        self.d_model      = d_model      or self.TRANSFORMER_DIM
        self.nhead        = nhead        or self.TRANSFORMER_HEADS
        self.num_layers   = num_layers   or self.TRANSFORMER_LAYERS
        self.dropout_rate = dropout      or self.DROPOUT_RATE
        self.window_size  = window_size  or self.WINDOW_SIZE

        self.encoder = nn.Linear(input_dim, self.d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(self.window_size, self.d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.nhead,
            dropout=self.dropout_rate,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=self.num_layers
        )

        self.decoder = nn.Linear(self.d_model, output_dim)

    def forward(self, x):
        # x: [batch, seq_len, input_dim]
        x = self.encoder(x)
        x = x + self.pos_encoder.unsqueeze(0)
        x = self.transformer_encoder(x)
        return self.decoder(x[:, -1, :])  # [batch, output_dim]


# ─── Helper to load state_dict models ──────────────────────────────────────────
BASE = Path(__file__).parent / "models"

def _load_ts_model(filename: str) -> nn.Module:
    path = BASE / filename
    ckpt = torch.load(path, map_location="cpu")
    if isinstance(ckpt, dict):
        enc_w = ckpt["encoder.weight"]
        dec_w = ckpt["decoder.weight"]
        in_d  = enc_w.size(1)
        out_d = dec_w.size(0)
        mdl = TimeSeriesTransformer(input_dim=in_d, output_dim=out_d)
        mdl.load_state_dict(ckpt)
        return mdl.eval()
    else:
        return ckpt.eval()

# Load all forecasting models
solar_model             = _load_ts_model("solar_model.pt")
wind_model              = _load_ts_model("wind_model.pt")
non_critical_load_model = _load_ts_model("non_critical_load_model.pt")
critical_load_model     = _load_ts_model("critical_load_model.pt")
essential_load_model    = _load_ts_model("essential_load_model.pt")

# ─── Prediction prep and helper ───────────────────────────────────────────────
def _prep(features: List[List[float]]) -> torch.Tensor:
    x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # [1,seq_len,input_dim]
    mean = x.mean(dim=1, keepdim=True)
    std  = x.std(dim=1, keepdim=True)
    return (x - mean) / (std + 1e-6)

# Prediction functions
def predict_solar(features: List[List[float]]) -> float:
    with torch.no_grad():
        return float(solar_model(_prep(features)).squeeze().item())

def predict_wind(features: List[List[float]]) -> float:
    with torch.no_grad():
        return float(wind_model(_prep(features)).squeeze().item())

def predict_non_critical_load(features: List[List[float]]) -> float:
    with torch.no_grad():
        return float(non_critical_load_model(_prep(features)).squeeze().item())

def predict_critical_load(features: List[List[float]]) -> float:
    with torch.no_grad():
        return float(critical_load_model(_prep(features)).squeeze().item())

def predict_essential_load(features: List[List[float]]) -> float:
    with torch.no_grad():
        return float(essential_load_model(_prep(features)).squeeze().item())


# ─── Forecast Loop ────────────────────────────────────────────────────────────
def run_forecast(
    df: pd.DataFrame,
    window_size: int = 10,
    forecast_horizon: int = 24
) -> pd.DataFrame:
    # Create scalers trained on historical data (replace with loaded scalers when available)
    solar_scaler      = MinMaxScaler().fit(df[['PVPCS_Active_Power']])
    wind_scaler       = MinMaxScaler().fit(df[['Wind_Power']])
    critical_scaler   = MinMaxScaler().fit(df[['Critical_Power_Load']])
    noncrit_scaler    = MinMaxScaler().fit(df[['Non_Critical_Power_Load']])
    essential_scaler  = MinMaxScaler().fit(df[['Essential_Power_Load']])

    targets = [
        {"name": "Solar",              "col": "PVPCS_Active_Power",      "model": predict_solar,           "scaler": solar_scaler      },
        {"name": "Wind",               "col": "Wind_Power",             "model": predict_wind,            "scaler": wind_scaler       },
        {"name": "Critical_Load",      "col": "Critical_Power_Load",    "model": predict_critical_load,   "scaler": critical_scaler   },
        {"name": "Non_Critical_Load",  "col": "Non_Critical_Power_Load","model": predict_non_critical_load,"scaler": noncrit_scaler    },
        {"name": "Essential_Load",     "col": "Essential_Power_Load",   "model": predict_essential_load,  "scaler": essential_scaler  }
    ]

    results = {}
    last_time = df.index[-1]

    # Run forecasting for each target
    for t in targets:
        # Prepare initial window
        values = df[t['col']].iloc[-window_size:].values.reshape(-1,1)
        scaled_vals = t['scaler'].transform(values).flatten().tolist()

        # Time features (hour sin/cos)
        times = df.index[-window_size:]
        hrs   = times.hour
        sin_seq = np.sin(2*np.pi*hrs/24).tolist()
        cos_seq = np.cos(2*np.pi*hrs/24).tolist()

        preds = []
        current_time = last_time
        for _ in range(forecast_horizon):
            seq = np.column_stack([scaled_vals, sin_seq, cos_seq])
            pred_scaled = t['model'](seq.tolist())
            pred_val = t['scaler'].inverse_transform([[pred_scaled]])[0,0]
            preds.append(pred_val)

            # Slide window
            current_time += pd.Timedelta(hours=1)
            scaled_vals.pop(0)
            sin_seq.pop(0)
            cos_seq.pop(0)
            scaled_vals.append(pred_scaled)
            sin_seq.append(np.sin(2*np.pi*current_time.hour/24))
            cos_seq.append(np.cos(2*np.pi*current_time.hour/24))

        results[f"{t['name']}_Pred"] = preds

    # Build forecast DataFrame
    forecast_index = pd.date_range(start=last_time+pd.Timedelta(hours=1), periods=forecast_horizon, freq='H')
    forecast_df = pd.DataFrame(results, index=forecast_index)
    forecast_df.index.name = 'Timestamp'
    return forecast_df.reset_index()


if __name__ == '__main__':
    # Load dataset
    df = pd.read_csv('/mnt/data/merged.csv')
    df.index = pd.date_range(start='2010-01-01', periods=len(df), freq='H')

    # Run and display forecast
    forecast_df = run_forecast(df, window_size=10, forecast_horizon=24)
    print(forecast_df.head())
