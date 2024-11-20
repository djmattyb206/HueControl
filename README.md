# 1. Install Required Library

Install `requests` if it’s not already installed.

```bash
pip install requests
```

---

# 2. Set Up

1. **Get your Hue Bridge IP address.**  
   Example: `192.168.8.238`

2. **Generate a user token** by pressing the Hue Bridge's physical button which makes an authenticated API request.

   Within a few seconds of pressing the button, run this code:

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
Note that the order of the lights in HueLights.json doesn't matter

---

# 4. Control the Hue Lights

1. Review the contents of `Colors.csv` for available color names and RGB values. You can also review the file named `Amazon Alexa Color Names and Examples and RGB code.pdf` to see a list of all the color names, their RGB values and a preview of the color. You may need to install the extension named "vscode-pdf" to corretly view the contents of the PDF file.

2. The Python script to control lights is HueControl.py

## Using HueControl.py
First specify the name of the light you want to control. Then specify a color name or an RGB value.

To specify a color name use:
 ```python
python HueControl.py "Computer Desk Left" --color_name "Coral"
   ```

To specify an RGB value use:
 ```python
python HueControl.py "Computer Desk Left" --rgb 255,69,0
   ```

# 5. Copy Light Settings

You can use the script `CopyLightSettings.py` to easily copy the current settings of one light to another light.

   ```python
import requests
import os
import json
import argparse

# Load bridge configuration from config.json
config_file = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_file, "r") as file:
    config = json.load(file)

bridge_ip = config["bridge_ip"]
username = config["username"]

# Load light IDs and names from HueLights.json
hue_lights_file = os.path.join(os.path.dirname(__file__), "HueLights.json")
with open(hue_lights_file, "r") as file:
    light_ids = {v: int(k) for k, v in json.load(file).items()}

# Function to get light's current color and brightness
def get_light_state(light_id):
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}"
    response = requests.get(url)
    if response.status_code == 200:
        light_data = response.json()
        state = light_data["state"]
        
        # Extract color and brightness information
        on_state = state["on"]
        brightness = state.get("bri", 254)  # Default to max if missing
        color_xy = state.get("xy", [0.0, 0.0])  # Default to [0.0, 0.0] if missing
        return on_state, brightness, color_xy
    else:
        print(f"Failed to retrieve state for light {light_id}: {response.status_code}, {response.text}")
        return None, None, None

# Function to set light's color and brightness
def set_light_state(light_id, on_state, brightness, color_xy):
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}/state"
    payload = {
        "on": on_state,
        "bri": brightness,
        "xy": color_xy
    }
    response = requests.put(url, json=payload)
    if response.status_code == 200:
        print(f"Set light {light_id} to match color and brightness")
    else:
        print(f"Failed to set light {light_id}: {response.status_code}, {response.text}")

# Main function to copy color and brightness from one light to another
def copy_light_state(source_light_name, target_light_name):
    source_light_id = light_ids.get(source_light_name)
    target_light_id = light_ids.get(target_light_name)

    if not source_light_id:
        print(f"Source light '{source_light_name}' not found.")
        return
    if not target_light_id:
        print(f"Target light '{target_light_name}' not found.")
        return

    # Get the color and brightness of the source light
    on_state, brightness, color_xy = get_light_state(source_light_id)
    if on_state is not None:
        # Set the target light to match the source light
        set_light_state(target_light_id, on_state, brightness, color_xy)
    else:
        print(f"Source light '{source_light_name}' state could not be retrieved.")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Copy settings from one Hue light to another.")
    parser.add_argument("source_light", type=str, help="The name of the light to copy settings from.")
    parser.add_argument("target_light", type=str, help="The name of the light to copy settings to.")
    args = parser.parse_args()

    # Execute the copy function with the provided arguments
    copy_light_state(args.source_light, args.target_light)


# Useage:
# python CopyLightSettings.py "Computer Desk Right" "Computer Desk Left"
   ```

To use it, you use the following syntax:

 ```python
python CopyLightSettings.py "Computer Desk Right" "Computer Desk Left"
   ```
