# 1. Install Required Library

Install `requests` if it’s not already installed.

```bash
pip install requests
```

---

# 2. Set Up

1. **Get your Hue Bridge IP address.**  
   Example: `192.168.8.238`

2. **Generate a user token** by pressing the Hue Bridge's physical button and making an authenticated API request.

   Example code:

   ```python
   # AuthenticatedApiControl.py
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
   ```

   **Expected response:**

   ```json
   [{"success":{"username":"new-username-generated"}}]
   ```

3. Save the information into a file named `config.json`:

   ```json
   {
       "bridge_ip": "192.168.0.238",
       "username": "new-username-generated"
   }
   ```

---

# 3. Python Script to Discover Light IDs

Use the following script to fetch all connected lights.

```python
# HueGetLightSettings.py
import requests
import json
import os

# Load configuration from config.json
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

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
```

Save the information into `HueLights.json`. Example:

```json
{
    "7": "Living Room 1",
    "9": "Living Room 2",
    "5": "Living Room 3",
    "8": "Living Room 4",
    "6": "Living Room 5",
    "10": "Living Room 6"
}
```

---

# 4. Control the Hue Lights

1. Review the contents of `Colors.csv` for available color names and RGB values.

2. Example Python script to control lights:

   ```python
   # HueControl.py
   ```

Review the file named `Amazon Alexa Color Names and Examples and RGB code.pdf` to see a list of all the color names and their RGB values. You may need to install the extension named "vscode-pdf" to corretly view the contents of the PDF file.

## Useage
First specify the name of the light you want to control. Then specify a color name or an RGB value.

To specify a color name use:
 ```python
python HueControl.py "Computer Desk Left" --color_name "Coral"
   ```

To specify an RGB value use:
 ```python
python HueControl.py "Computer Desk Left" --rgb 255,69,0
   ```
