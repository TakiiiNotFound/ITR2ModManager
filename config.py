import os
import json

# Determine the root folder of the application (where config.py is located)
ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Define the path for the configuration file in the root folder
CONFIG_FILE = os.path.join(ROOT_FOLDER, "config.json")

# Default configuration settings
DEFAULT_CONFIG = {
    "itr2_path": "",
    "temp_path": os.path.join(ROOT_FOLDER, "Temp")
}

def load_config():
    """
    Load the configuration from the config.json file.
    If the file doesn't exist, returns the default configuration.
    Also ensures that the Temp folder exists.
    """
    if not os.path.exists(CONFIG_FILE):
        config = DEFAULT_CONFIG.copy()
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # If any key is missing in the config, set it to the default value
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

    # Ensure the Temp folder exists
    ensure_temp_folder(config)
    return config

def save_config(config):
    """
    Save the given configuration dictionary to the config.json file.
    Also ensures that the Temp folder exists.
    """
    ensure_temp_folder(config)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def ensure_temp_folder(config):
    """
    Ensure that the Temp folder (as specified in the config) exists.
    """
    temp_path = config.get("temp_path", os.path.join(ROOT_FOLDER, "Temp"))
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

# Test the configuration functions when this script is run directly.
if __name__ == "__main__":
    # Load the current configuration (or defaults if no file exists)
    config = load_config()
    print("Current configuration:")
    print(json.dumps(config, indent=4))

    # Example: update the ITR2 path and save the configuration
    config["itr2_path"] = "C:/Path/To/ITR2"
    save_config(config)
    print("Configuration updated and saved.")
