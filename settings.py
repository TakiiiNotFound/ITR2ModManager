import json
import os
from tkinter import filedialog, Tk
import customtkinter as ctk  # For CTkToplevel popups

# Default configuration dictionary with AdvancedMode setting.
DEFAULT_CONFIG = {
    "ITR2_Path": "",
    "AdvancedMode": False
}

# Get the APPDATA path and define the configuration folder and file.
APPDATA_FOLDER = os.getenv("APPDATA")
CONFIG_FOLDER = os.path.join(APPDATA_FOLDER, "ITR2ModManager")

# Create the config folder if it does not exist.
if not os.path.exists(CONFIG_FOLDER):
    os.makedirs(CONFIG_FOLDER)

# Define the path to the configuration file.
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")

def load_config():
    """
    Load the configuration from config.json.
    If the file doesn't exist or is unreadable, create it with DEFAULT_CONFIG.
    
    Returns:
        dict: The configuration dictionary.
    """
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    # Ensure all default keys exist.
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    return config

def save_config(config):
    """
    Save the provided configuration dictionary to config.json.
    
    Args:
        config (dict): The configuration to save.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_ITR2_Path():
    """
    Get the current ITR2_Path from the configuration.
    
    Returns:
        str: The ITR2 game folder path.
    """
    config = load_config()
    return config.get("ITR2_Path", "")

def set_ITR2_Path(path):
    """
    Update the ITR2_Path in the configuration and save it.
    
    Args:
        path (str): The new ITR2 game folder path to store.
    """
    config = load_config()
    config["ITR2_Path"] = path
    save_config(config)

def get_AdvancedMode():
    """
    Get the current AdvancedMode setting from the configuration.
    
    Returns:
        bool: The state of AdvancedMode.
    """
    config = load_config()
    return config.get("AdvancedMode", False)

def set_AdvancedMode(state):
    """
    Update the AdvancedMode setting in the configuration and save it.
    
    Args:
        state (bool): The new state for AdvancedMode.
    """
    config = load_config()
    config["AdvancedMode"] = state
    save_config(config)

def select_ITR2_folder():
    """
    Open an explorer window to allow the user to select a folder.
    Updates the configuration with the selected folder and returns the folder path.
    
    Returns:
        str: The selected folder path.
    """
    # Create a temporary hidden Tk instance for the file dialog.
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select ITR2 Game Folder")
    root.destroy()
    if folder:
        set_ITR2_Path(folder)
    return folder

def show_popup(parent, message, title="Check Game Path"):
    """
    Create a popup window with the provided message using CTkToplevel,
    center it on the screen, set it as transient, and grab focus.
    
    Args:
        parent (ctk.CTk): The parent window.
        message (str): The message to display.
        title (str): The title for the popup window.
    """
    popup = ctk.CTkToplevel(parent)
    popup.title(title)
    width, height = 300, 100
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.transient(parent)
    popup.grab_set()
    popup.lift()
    label = ctk.CTkLabel(popup, text=message)
    label.pack(pady=10, padx=10)
    button = ctk.CTkButton(popup, text="OK", command=popup.destroy)
    button.pack(pady=(0,10))
    popup.wait_window(popup)

def check_game_path(parent):
    """
    Check the ITR2 game folder stored in config for the existence of:
      - A folder named "Engine"
      - A folder named "IntoTheRadius2"
      - A file named "IntoTheRadius2.exe"
    Shows a popup indicating whether the folder is correct.
    
    Args:
        parent (ctk.CTk): The parent window for the popup.
    
    Returns:
        bool: True if all items exist, False otherwise.
    """
    path = get_ITR2_Path()
    if not path:
        show_popup(parent, "Game Folder incorrect: no path set!")
        return False

    engine_exists = os.path.isdir(os.path.join(path, "Engine"))
    itr_exists = os.path.isdir(os.path.join(path, "IntoTheRadius2"))
    exe_exists = os.path.isfile(os.path.join(path, "IntoTheRadius2.exe"))
    
    if engine_exists and itr_exists and exe_exists:
        show_popup(parent, "Correct Game Folder!")
        return True
    else:
        show_popup(parent, "Game Folder incorrect")
        return False
