import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import config

def select_itr2_folder():
    """
    Opens a folder selection dialog for the ITR2 Game folder.
    If a folder is selected, converts the path to a Windows-style path 
    with backslashes and lowercase letters, updates the configuration's itr2_path,
    and returns the selected folder path.
    """
    root = tk.Tk()
    root.withdraw()  
    folder_selected = filedialog.askdirectory(title="Select ITR2 Game folder")
    root.destroy()
    
    if folder_selected:
        folder_selected = os.path.normpath(folder_selected).lower()
        cfg = config.load_config()
        cfg["itr2_path"] = folder_selected
        config.save_config(cfg)
        return folder_selected
    return None

def select_temp_folder():
    """
    Opens a folder selection dialog for the Temp folder.
    If a folder is selected, converts the path to a Windows-style path 
    with backslashes and lowercase letters, updates the configuration's temp_path,
    and returns the selected folder path.
    """
    root = tk.Tk()
    root.withdraw()  
    folder_selected = filedialog.askdirectory(title="Select Temp folder")
    root.destroy()
    
    if folder_selected:
        folder_selected = os.path.normpath(folder_selected).lower()
        cfg = config.load_config()
        cfg["temp_path"] = folder_selected
        config.save_config(cfg)
        return folder_selected
    return None

def clear_temp_folder():
    """
    Deletes everything inside the Temp folder specified in the configuration.
    Ignores any files or directories that fail to delete.
    """
    cfg = config.load_config()
    temp_path = cfg.get("temp_path")
    if not temp_path or not os.path.exists(temp_path):
        return
    
    for filename in os.listdir(temp_path):
        file_path = os.path.join(temp_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)
        except Exception:
            pass

def open_fomod_folder():
    """
    Opens the Fomod Creation Tool folder located at <rootfolder>/Fomod.
    If the folder does not exist, it is created.
    """
    root_folder = os.path.dirname(os.path.abspath(config.__file__))
    fomod_folder = os.path.join(root_folder, "Fomod")
    if not os.path.exists(fomod_folder):
        os.makedirs(fomod_folder)
    try:
        os.startfile(fomod_folder)
    except Exception as e:
        print(f"Error opening folder: {e}")

def check_itr2_game_folder(path):
    """
    Checks if the provided path is a valid ITR2 game folder.
    It must contain:
      - A folder named "Engine"
      - A folder named "IntoTheRadius2"
      - A file named "IntoTheRadius2.exe"
    
    Displays a popup indicating success or error.
    """
    if not path:
        messagebox.showerror("Error", "No path provided.")
        return False
    engine_path = os.path.join(path, "Engine")
    itr2_folder = os.path.join(path, "IntoTheRadius2")
    exe_path = os.path.join(path, "IntoTheRadius2.exe")
    if os.path.isdir(engine_path) and os.path.isdir(itr2_folder) and os.path.isfile(exe_path):
        messagebox.showinfo("Success", "Game folder correct.")
        return True
    else:
        messagebox.showerror(
            "Error",
            "Into The Radius 2 could not be found... please make sure to select the root of your game folder *where IntoTheRadius2.exe is*"
        )
        return False

# Example usage (for testing this module independently)
if __name__ == "__main__":
    print("Select ITR2 Game folder:")
    print(select_itr2_folder())
    print("Select Temp folder:")
    print(select_temp_folder())
    print("Clearing Temp folder...")
    clear_temp_folder()
    print("Opening Fomod folder...")
    open_fomod_folder()
