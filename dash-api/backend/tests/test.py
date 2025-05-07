import requests

BASE = "http://localhost:8000"

# input dimensions for each model
MODEL_DIMS = {
    "solar": 7,
    "wind": 7,
    "non_critical_load": 6,
    "critical_load": 6,
    "essential_load": 6,
}

def test_forecast(name: str):
    dim = MODEL_DIMS[name]
    # window_size=10, each step has `dim` features
    features = [
        [i * 0.1 + j * 0.01 for j in range(dim)]
        for i in range(10)
    ]
    r = requests.post(f"{BASE}/forecast/{name}", json={"features": features})
    print(f"{name.upper():20} → {r.status_code} {r.json()}")

def test_rl():
    # must match your PPO agent's obs_dim (32)
    state = [i * 0.1 for i in range(32)]
    r = requests.post(f"{BASE}/rl/action", json={"state": state})
    print(f"{'RL ACTION':20} → {r.status_code} {r.json()}")

if __name__ == "__main__":
    print("🔍 Testing Microgrid API")
    for name in MODEL_DIMS:
        test_forecast(name)
    test_rl()