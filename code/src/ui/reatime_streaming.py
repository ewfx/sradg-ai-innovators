import requests
import json

import requests
import json

url = "http://127.0.0.1:8000/realtime_anomaly/"
data = {
        "TRADEID": 123,
        "RISKDATE": "2023-10-26T10:00:00",
        "DESKNAME": "DeskA",
        "QUANTITYDIFFERENCE": 15.0,
        "IMPACT_PRICE": 100.0,
        "IMPACT_QUANTITY": 5.0,
        "COMMENT": "Data entry error"
    }


headers = {"Content-Type": "application/json"}
print("calling realtime_anomaly")
response = requests.post(url, data=json.dumps(data), headers=headers)

print(f"Response status code: {response.status_code}")
try:
    print(f"Response JSON: {response.json()}")
except json.JSONDecodeError:
    print(f"Response text: {response.text}")
