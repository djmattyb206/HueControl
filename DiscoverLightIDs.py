import requests
import json
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to config.json
config_path = os.path.join(script_dir, "config.json")

# Load configuration from config.json
with open(config_path, "r") as config_file:
    config = json.load(config_file)

bridge_ip = config["bridge_ip"]
username = config["username"]
url = f"http://{bridge_ip}/api/{username}/lights"

response = requests.get(url)
if response.status_code == 200:
    lights = response.json()
    for light_id, light_info in lights.items():
        print(f"Light ID: {light_id}")
        print(f"Name: {light_info['name']}")
        print(f"State: {'On' if light_info['state']['on'] else 'Off'}")
        print(f"Brightness: {light_info['state']['bri']}")
        print()
else:
    print("Failed to retrieve lights:", response.status_code, response.text)
