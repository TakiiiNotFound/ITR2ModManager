import json
import os

# Get the AppData\Roaming directory for the current user.
APPDATA = os.getenv("APPDATA")

# Configuration file path: C:\Users\<username>\AppData\Roaming\ITR2ModManager\config.json
CONFIG_PATH = os.path.join(APPDATA, "ITR2ModManager", "config.json")

# Default configuration dictionary with:
#  - itr2_path: Empty by default (to be set by the user)
#  - temp_path: C:\Users\<username>\AppData\Roaming\ITR2ModManager\temp
#  - fomod_path: C:\Users\<username>\AppData\Roaming\ITR2ModManager\Fomod
DEFAULT_CONFIG = {
    "itr2_path": "",
    "temp_path": os.path.join(APPDATA, "ITR2ModManager", "temp"),
    "fomod_path": os.path.join(APPDATA, "ITR2ModManager", "Fomod")
}

def load_config():
    """
    Loads the configuration from CONFIG_PATH.
    If the file does not exist or if there is an error, 
    writes and returns the default configuration.
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config_data = json.load(f)
            return config_data
        except Exception as e:
            print("Error loading configuration:", e)
            # Fallback to default configuration
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    """
    Saves the given configuration dictionary to CONFIG_PATH.
    Automatically creates the directory if it does not exist.
    """
    try:
        directory = os.path.dirname(CONFIG_PATH)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print("Error saving configuration:", e)

if __name__ == "__main__":
    # Test configuration loading and saving
    cfg = load_config()
    print("Configuration loaded:")
    print(cfg)
    # Example: change a value and save it
    cfg["itr2_path"] = r"C:\Path\To\ITR2"
    save_config(cfg)
    print("Configuration updated.")
