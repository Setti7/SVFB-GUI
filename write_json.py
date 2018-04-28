import json

key = "C"
data = {"Version": 1.0,
        "Date": "2018-04-19",
        "Used key": key,
        "User": "Anon",
        "Password": "idk",
        "Auto-send": True,
        }

with open('config.txt', 'w') as f:
    json.dump(data, f)
