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
