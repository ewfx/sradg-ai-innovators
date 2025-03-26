import requests
import json

import requests
import json

url = "http://127.0.0.1:8000/batch_anomaly/"
data = [
    {
        "TRADEID": 123,
        "RISKDATE": "2023-10-26T10:00:00",
        "DESKNAME": "DeskA",
        "QUANTITYDIFFERENCE": 15.0,
        "IMPACT_PRICE": 100.0,
        "IMPACT_QUANTITY": 5.0,
        "COMMENT": "Data entry error"
    },
    {
        "TRADEID": 456,
        "RISKDATE": "2023-10-27T11:00:00",
        "DESKNAME": "DeskB",
        "QUANTITYDIFFERENCE": 2.0,
        "IMPACT_PRICE": 50.0,
        "IMPACT_QUANTITY": 1.0,
        "COMMENT": "Rounding error"
    },
      {
    "TRADEID": 789,
    "RISKDATE": "2024-03-20T14:30:00",
    "DESKNAME": "DeskC",
    "QUANTITYDIFFERENCE": 50.0,
    "IMPACT_PRICE": 200.0,
    "IMPACT_QUANTITY": 10.0,
    "COMMENT": "Large quantity difference, potential manual error"
  },
  {
    "TRADEID": 101,
    "RISKDATE": "2024-03-21T09:15:00",
    "DESKNAME": "DeskA",
    "QUANTITYDIFFERENCE": -30.0,
    "IMPACT_PRICE": 150.0,
    "IMPACT_QUANTITY": -6.0,
    "COMMENT": "Negative impact, review required"
  },
    {
    "TRADEID": 202,
    "RISKDATE": "2024-03-22T11:45:00",
    "DESKNAME": "DeskB",
    "QUANTITYDIFFERENCE": 25.0,
    "IMPACT_PRICE": 180.0,
    "IMPACT_QUANTITY": 7.0,
    "COMMENT": "Unusual quantity difference, needs investigation"
  },
    {
    "TRADEID": 303,
    "RISKDATE": "2024-03-23T13:20:00",
    "DESKNAME": "DeskC",
    "QUANTITYDIFFERENCE": -40.0,
    "IMPACT_PRICE": 220.0,
    "IMPACT_QUANTITY": -9.0,
    "COMMENT": "Significant negative impact, immediate review"
  },
  {
    "TRADEID": 404,
    "RISKDATE": "2024-03-24T10:00:00",
    "DESKNAME": "DeskA",
    "QUANTITYDIFFERENCE": 60.0,
    "IMPACT_PRICE": 250.0,
    "IMPACT_QUANTITY": 12.0,
    "COMMENT": "Extremely high quantity difference, urgent review"
  }

]


headers = {"Content-Type": "application/json"}
print("calling batch_anomaly")
response = requests.post(url, data=json.dumps(data), headers=headers)

print(f"Response status code: {response.status_code}")
try:
    print(f"Response JSON: {response.json()}")
except json.JSONDecodeError:
    print(f"Response text: {response.text}")
