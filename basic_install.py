import os
import shutil
import zipfile
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import config

def basic_install():
    # Create the main window
    root = tk.Tk()
    root.title("Basic Mod Install")
    root.geometry("400x300")
    root.configure(bg="#171717")
    
    # Set the window icon from %APPDATA%\ITR2ModManager\ITR2MM.ico
    appdata = os.getenv("APPDATA")
    icon_path = os.path.join(appdata, "ITR2ModManager", "ITR2MM.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception as e:
            print("Error setting icon:", e)
    
    # Step 1: Open an explorer window to select a mod archive.
    archive_path = filedialog.askopenfilename(
        parent=root,
        title="Select mod archive (.zip, .rar, .7z)",
        filetypes=[("Zip files", "*.zip"), ("RAR files", "*.rar"), ("7z files", "*.7z")]
    )
    if not archive_path:
        messagebox.showinfo("Cancelled", "No archive selected", parent=root)
        root.destroy()
        return
    
    # Step 2: Ask the user to input the mod name.
    mod_name = simpledialog.askstring("Mod Name", "Enter mod name:", parent=root)
    if not mod_name:
        messagebox.showinfo("Cancelled", "No mod name provided", parent=root)
        root.destroy()
        return
    
    # Retrieve configuration for ITR2 installation and temporary folder.
    cfg = config.load_config()
    itr2_path = cfg.get("itr2_path")
    temp_path = cfg.get("temp_path")
    if not itr2_path:
        messagebox.showerror("Error", "ITR2 path not configured", parent=root)
        root.destroy()
        return

    # Ensure the temporary folder exists.
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    # Create the mod installation folder (inside Mods folder under ITR2 installation)
    mod_install_folder = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods", mod_name)
    os.makedirs(mod_install_folder, exist_ok=True)
    
    # Create a temporary extraction folder within temp_path.
    temp_mod_folder = tempfile.mkdtemp(prefix="mod_", dir=temp_path)
    
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(temp_mod_folder)
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Failed to extract archive:\n{str(e)}", parent=root)
        shutil.rmtree(temp_mod_folder)
        root.destroy()
        return

    # Move all mod files (.pak, .utoc, .ucas) from the extracted folder to the mod_install_folder.
    found = False
    for root_dir, dirs, files in os.walk(temp_mod_folder):
        for file in files:
            if file.lower().endswith((".pak", ".utoc", ".ucas")):
                src = os.path.join(root_dir, file)
                dst = os.path.join(mod_install_folder, file)
                try:
                    shutil.move(src, dst)
                    found = True
                except Exception as e:
                    messagebox.showerror("File Move Error", f"Error moving {src}:\n{str(e)}", parent=root)
    
    if found:
        messagebox.showinfo("Success", "Mod installed successfully!", parent=root)
    else:
        messagebox.showerror("Error", "No mod files (.pak, .utoc, .ucas) were found in the archive.", parent=root)
    
    # Clean up the temporary extraction folder.
    shutil.rmtree(temp_mod_folder)
    root.destroy()

if __name__ == "__main__":
    basic_install()
