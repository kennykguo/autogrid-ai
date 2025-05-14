# import torch
# from typing import List
# from pathlib import Path
# import torch.nn as nn

# # ─── Model definition ─────────────────────────────────────────────────────────
# class TimeSeriesTransformer(nn.Module):
#     WINDOW_SIZE        = 10
#     TRANSFORMER_DIM    = 64
#     TRANSFORMER_HEADS  = 4
#     TRANSFORMER_LAYERS = 2
#     DROPOUT_RATE       = 0.1

#     def __init__(
#         self,
#         input_dim: int,
#         output_dim: int,
#         d_model: int     = None,
#         nhead: int       = None,
#         num_layers: int  = None,
#         dropout: float   = None,
#         window_size: int = None,
#     ):
#         super().__init__()
#         self.d_model      = d_model      or self.TRANSFORMER_DIM
#         self.nhead        = nhead        or self.TRANSFORMER_HEADS
#         self.num_layers   = num_layers   or self.TRANSFORMER_LAYERS
#         self.dropout_rate = dropout      or self.DROPOUT_RATE
#         self.window_size  = window_size  or self.WINDOW_SIZE

#         self.encoder = nn.Linear(input_dim, self.d_model)
#         self.pos_encoder = nn.Parameter(torch.zeros(self.window_size, self.d_model))

#         encoder_layer = nn.TransformerEncoderLayer(
#             d_model=self.d_model,
#             nhead=self.nhead,
#             dropout=self.dropout_rate,
#             batch_first=True
#         )
#         self.transformer_encoder = nn.TransformerEncoder(
#             encoder_layer,
#             num_layers=self.num_layers
#         )

#         self.decoder = nn.Linear(self.d_model, output_dim)

#     def forward(self, x):
#         # x: [batch_size, seq_len, input_dim]
#         x = self.encoder(x)
#         x = x + self.pos_encoder.unsqueeze(0)
#         x = self.transformer_encoder(x)
#         return self.decoder(x[:, -1, :])  # [batch_size, output_dim]


# # ─── Load models ──────────────────────────────────────────────────────────────
# BASE = Path(__file__).parent / "models"

# def _load_model(file: Path) -> nn.Module:
#     ckpt = torch.load(file, map_location="cpu")
#     if isinstance(ckpt, dict):
#         enc_w = ckpt["encoder.weight"]
#         dec_w = ckpt["decoder.weight"]
#         in_d  = enc_w.size(1)
#         out_d = dec_w.size(0)
#         m = TimeSeriesTransformer(input_dim=in_d, output_dim=out_d)
#         m.load_state_dict(ckpt)
#         return m
#     else:
#         return ckpt

# solar_model = _load_model(BASE / "solar_model.pt").eval()
# wind_model  = _load_model(BASE / "wind_model.pt").eval()


# # ─── Prediction ───────────────────────────────────────────────────────────────
# def predict_solar(features: List[List[float]]) -> float:
#     """
#     features: nested list of shape [window_size][input_dim]
#     """
#     x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # [1, seq, feat]
#     with torch.no_grad():
#         return float(solar_model(x).item())

# def predict_wind(features: List[List[float]]) -> float:
#     x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
#     with torch.no_grad():
#         return float(wind_model(x).item())



# import torch
# from typing import List
# from pathlib import Path
# import torch.nn as nn

# # ─── Model definition ─────────────────────────────────────────────────────────
# class TimeSeriesTransformer(nn.Module):
#     WINDOW_SIZE        = 10
#     TRANSFORMER_DIM    = 64
#     TRANSFORMER_HEADS  = 4
#     TRANSFORMER_LAYERS = 2
#     DROPOUT_RATE       = 0.1

#     def __init__(
#         self,
#         input_dim: int,
#         output_dim: int,
#         d_model: int     = None,
#         nhead: int       = None,
#         num_layers: int  = None,
#         dropout: float   = None,
#         window_size: int = None,
#     ):
#         super().__init__()
#         self.d_model      = d_model      or self.TRANSFORMER_DIM
#         self.nhead        = nhead        or self.TRANSFORMER_HEADS
#         self.num_layers   = num_layers   or self.TRANSFORMER_LAYERS
#         self.dropout_rate = dropout      or self.DROPOUT_RATE
#         self.window_size  = window_size  or self.WINDOW_SIZE

#         self.encoder = nn.Linear(input_dim, self.d_model)
#         self.pos_encoder = nn.Parameter(torch.zeros(self.window_size, self.d_model))

#         encoder_layer = nn.TransformerEncoderLayer(
#             d_model=self.d_model,
#             nhead=self.nhead,
#             dropout=self.dropout_rate,
#             batch_first=True
#         )
#         self.transformer_encoder = nn.TransformerEncoder(
#             encoder_layer,
#             num_layers=self.num_layers
#         )

#         self.decoder = nn.Linear(self.d_model, output_dim)

#     def forward(self, x):
#         # x: [batch, seq_len, input_dim]
#         x = self.encoder(x)
#         x = x + self.pos_encoder.unsqueeze(0)
#         x = self.transformer_encoder(x)
#         return self.decoder(x[:, -1, :])  # [batch, output_dim]


# # ─── Helper to load either state_dict or full model ───────────────────────────
# BASE = Path(__file__).parent / "models"

# def _load_ts_model(filename: str) -> nn.Module:
#     path = BASE / filename
#     ckpt = torch.load(path, map_location="cpu")
#     if isinstance(ckpt, dict):
#         enc_w = ckpt["encoder.weight"]
#         dec_w = ckpt["decoder.weight"]
#         in_d  = enc_w.size(1)
#         out_d = dec_w.size(0)
#         mdl = TimeSeriesTransformer(input_dim=in_d, output_dim=out_d)
#         mdl.load_state_dict(ckpt)
#         return mdl
#     else:
#         return ckpt

# # load all forecasting models
# solar_model             = _load_ts_model("solar_model.pt").eval()
# wind_model              = _load_ts_model("wind_model.pt").eval()
# non_critical_load_model = _load_ts_model("non_critical_load_model.pt").eval()
# critical_load_model     = _load_ts_model("critical_load_model.pt").eval()
# essential_load_model    = _load_ts_model("essential_load_model.pt").eval()


# # ─── Prediction functions ──────────────────────────────────────────────────────
# def _prep(features: List[List[float]]) -> torch.Tensor:
#     """ Convert nested list [window_size][input_dim] → tensor [1,window_size,input_dim] """
#     x = torch.tensor(features, dtype=torch.float32)
#     return x.unsqueeze(0)

# def predict_solar(features: List[List[float]]) -> float:
#     with torch.no_grad():
#         return float(solar_model(_prep(features)).item())

# def predict_wind(features: List[List[float]]) -> float:
#     with torch.no_grad():
#         return float(wind_model(_prep(features)).item())

# def predict_non_critical_load(features: List[List[float]]) -> float:
#     with torch.no_grad():
#         return float(non_critical_load_model(_prep(features)).item())

# def predict_critical_load(features: List[List[float]]) -> float:
#     with torch.no_grad():
#         return float(critical_load_model(_prep(features)).item())

# def predict_essential_load(features: List[List[float]]) -> float:
#     with torch.no_grad():
#         return float(essential_load_model(_prep(features)).item())



import torch
from typing import List
from pathlib import Path
import torch.nn as nn

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


# ─── Helper to load either state_dict or full model ───────────────────────────
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
        return mdl
    else:
        return ckpt

# load all forecasting models
solar_model             = _load_ts_model("solar_model.pt").eval()
wind_model              = _load_ts_model("wind_model.pt").eval()
non_critical_load_model = _load_ts_model("non_critical_load_model.pt").eval()
critical_load_model     = _load_ts_model("critical_load_model.pt").eval()
essential_load_model    = _load_ts_model("essential_load_model.pt").eval()


# ─── Prediction functions ──────────────────────────────────────────────────────
def _prep(features: List[List[float]]) -> torch.Tensor:
    """
    Convert nested list [window_size][input_dim] →
    zero‐mean, unit‐variance normalized tensor [1,window_size,input_dim]
    """
    x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # [1,seq_len,input_dim]
    # normalize per-feature across the sequence axis
    mean = x.mean(dim=1, keepdim=True)   # [1,1,input_dim]
    std  = x.std(dim=1, keepdim=True)    # [1,1,input_dim]
    return (x - mean) / (std + 1e-6)


def predict_solar(features: List[List[float]]) -> float:
    x = _prep(features)
    with torch.no_grad():
        y = solar_model(x)
    y = y.squeeze()  # remove batch/output dims
    return float(y.item())  # scalar


def predict_wind(features: List[List[float]]) -> float:
    x = _prep(features)
    with torch.no_grad():
        y = wind_model(x)
    y = y.squeeze()
    return float(y.item())


def predict_non_critical_load(features: List[List[float]]) -> float:
    x = _prep(features)
    with torch.no_grad():
        y = non_critical_load_model(x)
    y = y.squeeze()
    return float(y.item())


def predict_critical_load(features: List[List[float]]) -> float:
    x = _prep(features)
    with torch.no_grad():
        y = critical_load_model(x)
    y = y.squeeze()
    return float(y.item())


def predict_essential_load(features: List[List[float]]) -> float:
    x = _prep(features)
    with torch.no_grad():
        y = essential_load_model(x)
    y = y.squeeze()
    return float(y.item())
