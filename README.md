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

```python
import requests
import csv
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

# Function to read RGB values from Colors.csv
def get_rgb_from_color_name(color_name):
    csv_file = os.path.join(os.path.dirname(__file__), "Colors.csv")
    with open(csv_file, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Name"].strip().lower() == color_name.strip().lower():
                return int(row["Red"]), int(row["Green"]), int(row["Blue"])
    return None

# Function to convert RGB to XY (Hue color space)
def rgb_to_xy(red, green, blue):
    r, g, b = [x / 255.0 for x in (red, green, blue)]
    r = pow((r + 0.055) / 1.055, 2.4) if r > 0.04045 else r / 12.92
    g = pow((g + 0.055) / 1.055, 2.4) if g > 0.04045 else g / 12.92
    b = pow((b + 0.055) / 1.055, 2.4) if b > 0.04045 else b / 12.92
    x = r * 0.664511 + g * 0.154324 + b * 0.162028
    y = r * 0.283881 + g * 0.668433 + b * 0.047685
    z = r * 0.000088 + g * 0.072310 + b * 0.986039
    return round(x / (x + y + z), 4), round(y / (x + y + z), 4)

# Function to set specified light to specified color
def set_light_to_color(light_name, color_name=None, rgb=None):
    light_id = light_ids.get(light_name)
    if not light_id:
        print(f"Light '{light_name}' not found.")
        return

    if color_name:
        rgb = get_rgb_from_color_name(color_name)
        if not rgb:
            print(f"Color '{color_name}' not found.")
            return
    elif not rgb:
        print("You must provide either a color name or RGB values.")
        return

    xy = rgb_to_xy(*rgb)
    
    url = f"http://{bridge_ip}/api/{username}/lights/{light_id}/state"
    payload = {
        "on": True,
        "xy": xy,
        "bri": 254  # Maximum brightness
    }
    response = requests.put(url, json=payload)
    if response.status_code == 200:
        print(f"Set '{light_name}' to color {rgb if not color_name else color_name}")
    else:
        print(f"Failed to set '{light_name}' to color {rgb if not color_name else color_name}: {response.text}")

# Main function to handle command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set a Hue light to a specific color.")
    parser.add_argument("light_name", type=str, help="The name of the light to control.")
    parser.add_argument("--color_name", type=str, help="The color name to set the light to.")
    parser.add_argument("--rgb", type=str, help="The RGB values (comma-separated, e.g., 255,0,0) to set the light to.")
    args = parser.parse_args()

    if args.rgb:
        rgb_values = tuple(map(int, args.rgb.split(",")))
        if len(rgb_values) == 3 and all(0 <= val <= 255 for val in rgb_values):
            set_light_to_color(args.light_name, rgb=rgb_values)
        else:
            print("Invalid RGB values. Please provide three integers between 0 and 255.")
    elif args.color_name:
        set_light_to_color(args.light_name, color_name=args.color_name)
    else:
        print("You must specify either a color name or RGB values.")

# Useage: 
# python HueControl.py "Computer Desk Left" --color_name "Coral"
# python HueControl.py "Computer Desk Left" --rgb 255,69,0
```

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
