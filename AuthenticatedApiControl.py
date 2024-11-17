import requests
import json

bridge_ip = "192.168.0.238"
url = f"http://{bridge_ip}/api"

payload = {"devicetype": "my_hue_app"}

response = requests.post(url, json=payload)
if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Failed to create username:", response.status_code, response.text)
