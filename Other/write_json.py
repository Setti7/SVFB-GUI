import json

data = {"Version": 1.0,
        "Date": "2018-04-25",
        "Used key": "C",
        "Resolution": "1280x720",
        "Zoom": 2,
        "Auto-send": True,
        "User": "Anon",
        "Password": "idk"
        }

with open('config.json', 'w') as f:
    json.dump(data, f)
