import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import config

def basic_install():
    # Step 1: Let the user select a zip file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select mod archive (.zip, .rar, .7z)",
        filetypes=[("Zip files", "*.zip"), ("RAR files", "*.rar"), ("7z files", "*.7z")]
    )
    if not file_path:
        messagebox.showinfo("Cancelled", "No file was selected.")
        return

    # For simplicity, only process zip files
    if not file_path.lower().endswith(".zip"):
        messagebox.showerror("Unsupported file", "Only .zip files are supported in this example.")
        return

    # Step 2: Ask for the mod name
    mod_name = simpledialog.askstring("Mod Name", "Enter mod name:")
    if not mod_name:
        messagebox.showerror("Error", "No mod name provided.")
        return

    # Load configuration to get the temp folder and ITR2 path
    cfg = config.load_config()
    temp_folder = cfg.get("temp_path")
    itr2_path = cfg.get("itr2_path")
    if not itr2_path or not os.path.exists(itr2_path):
        messagebox.showerror("Error", "ITR2 path is not configured correctly.")
        return

    # Step 3: Create target folders in both temp and install directories
    mod_temp_folder = os.path.join(temp_folder, mod_name)
    mod_install_folder = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods", mod_name)

    try:
        os.makedirs(mod_temp_folder, exist_ok=True)
        os.makedirs(mod_install_folder, exist_ok=True)

        # Step 4: Extract the zip into the temp mod folder
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(mod_temp_folder)

        # Step 5: Find and move all .pak, .ucas, .utoc files from the extracted content
        found_files = []
        for root_dir, dirs, files in os.walk(mod_temp_folder):
            for file in files:
                if file.lower().endswith(('.pak', '.ucas', '.utoc')):
                    src_file = os.path.join(root_dir, file)
                    shutil.move(src_file, os.path.join(mod_install_folder, file))
                    found_files.append(file)

        if not found_files:
            messagebox.showerror("Error", "No .pak, .ucas or .utoc files were found in the archive.")
            return

        # Step 6: Create an empty "mod" file in the install folder
        mod_file_path = os.path.join(mod_install_folder, "mod")
        with open(mod_file_path, "w") as f:
            f.write("")

        # Clean up the temp mod folder
        shutil.rmtree(mod_temp_folder)

        # Step 7: Success message
        messagebox.showinfo("Success", "Mod installed successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        if os.path.exists(mod_temp_folder):
            shutil.rmtree(mod_temp_folder)

if __name__ == "__main__":
    basic_install()
