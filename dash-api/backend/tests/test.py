# import pytest
# import requests

# # base URL of your forecasting API\BASE_URL = "http://localhost:8000"  # adjust as needed

# @pytest.fixture
# def base_url():
#     return "http://localhost:8000"  # change port/path if different


# def test_next_hour_forecast(base_url):
#     """
#     Test that the /forecast endpoint returns the next-hour forecast correctly.
#     """
#     # request only the next-hour forecast (horizon=1)
#     response = requests.get(f"{base_url}/forecast", params={"horizon": 1})
#     assert response.status_code == 200, "status code should be 200 OK"

#     data = response.json()
#     # expect a list with a single forecast entry
#     assert isinstance(data, list), "response should be a list"
#     assert len(data) == 1, "should return exactly one forecast record"

#     entry = data[0]
#     # required fields in the forecast entry
#     expected_fields = {
#         "Timestamp",
#         "Solar_Pred",
#         "Wind_Pred",
#         "Critical_Load_Pred",
#         "Non_Critical_Load_Pred",
#         "Essential_Load_Pred",
#     }
#     assert expected_fields.issubset(entry.keys()), "missing one or more forecast fields"

#     # verify field types
#     # Timestamp should be a string in ISO format
#     timestamp = entry["Timestamp"]
#     assert isinstance(timestamp, str), "Timestamp should be a string"
#     # Predictions should be numeric
#     for field in expected_fields - {"Timestamp"}:
#         val = entry[field]
#         assert isinstance(val, (int, float)), f"{field} should be numeric"

# if __name__ == "__main__":
#     pytest.main()

# import requests

# BASE_URL = "http://localhost:8000"

# def fetch_next_forecast():
#     url = f"{BASE_URL}/forecast/next"
#     try:
#         resp = requests.get(url)
#         resp.raise_for_status()
#         data = resp.json()
#         print("Next-hour forecast:")
#         for k, v in data.items():
#             print(f"  {k}: {v}")
#         return data
#     except requests.exceptions.RequestException as e:
#         print(f"Forecast request failed: {e}")
#         print(resp.text if 'resp' in locals() else "")
#         return None

# def fetch_rl_action(state: list):
#     url = f"{BASE_URL}/rl/action"
#     payload = {"state": state}
#     try:
#         resp = requests.post(url, json=payload)
#         resp.raise_for_status()
#         data = resp.json()
#         print("RL agent action:")
#         print(f"  action: {data['action']}")
#         return data["action"]
#     except requests.exceptions.RequestException as e:
#         print(f"RL request failed: {e}")
#         print(resp.text if 'resp' in locals() else "")
#         return None

# if __name__ == "__main__":
#     # 1) Get the next‐hour forecast
#     forecast = fetch_next_forecast()
#     if not forecast:
#         exit(1)

#     # 2) Build the state vector from the forecast
#     state = [
#         forecast["Solar_Pred"],
#         forecast["Wind_Pred"],
#         forecast["Non_Critical_Pred"],
#         forecast["Critical_Pred"],
#         forecast["Essential_Pred"],
#     ]

#     # 3) Send that list to /rl/action
#     agent_action = fetch_rl_action(state)

import requests

BASE_URL = "http://localhost:8000"

def fetch_next_forecast():
    r = requests.get(f"{BASE_URL}/forecast/next")
    r.raise_for_status()
    return r.json()

def fetch_rl_action():
    r = requests.post(f"{BASE_URL}/rl/action")
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    forecast = fetch_next_forecast()
    print("Forecast:", forecast)

    result = fetch_rl_action()
    print("RL action result:")
    print("  forecast:", result["forecast"])
    print("  action:", result["action"])