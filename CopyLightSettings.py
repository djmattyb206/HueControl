import requests
import os
import json

# Load bridge configuration from config.json
config_file = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_file, "r") as file:
    config = json.load(file)

bridge_ip = config["bridge_ip"]
username = config["username"]

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
def copy_light_state(source_light_id, target_light_id):
    # Get the color and brightness of the source light
    on_state, brightness, color_xy = get_light_state(source_light_id)
    if on_state is not None:
        # Set the target light to match the source light
        set_light_state(target_light_id, on_state, brightness, color_xy)
    else:
        print("Source light state could not be retrieved.")

# Example usage
source_light_id = 16  # Replace with the source light ID (e.g., "Computer Desk Right")
target_light_id = 18  # Replace with the target light ID (e.g., "Computer Desk Left")
copy_light_state(source_light_id, target_light_id)
