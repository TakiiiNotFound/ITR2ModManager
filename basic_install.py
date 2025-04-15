import os
import re
import zipfile
import customtkinter as ctk
from tkinter import filedialog, messagebox
import settings

def open_basic_install_window(parent):
    """
    Open a new, non‑resizable window (800x600) for Basic Mod Install.
    The window appears on top of the main window and shows a label and a "Select" button to choose a .zip file.
    """
    basic_win = ctk.CTkToplevel(parent)
    basic_win.title("Basic Install")
    basic_win.geometry("800x600")
    basic_win.resizable(False, False)
    basic_win.transient(parent)
    basic_win.grab_set()
    basic_win.lift(parent)
    
    label = ctk.CTkLabel(basic_win, text="Select the mod", font=("Arial", 16))
    label.pack(pady=20)
    
    def select_zip_file():
        file_path = filedialog.askopenfilename(
            title="Select Mod Zip File",
            filetypes=[("ZIP Files", "*.zip")]
        )
        if file_path:
            install_mod(file_path, basic_win)
    
    select_button = ctk.CTkButton(basic_win, text="Select", command=select_zip_file)
    select_button.pack(pady=10)
    
    return basic_win

def install_mod(zip_file_path, window):
    """
    Install the mod from the provided zip file.
    
    For each file in the zip, the relative path is adjusted as follows:
      - If the zip entry's path has at least two parts and its second component equals one of
        "Mods", "LogicMods", or "LuaMods" (case‑insensitive), then that folder name is removed.
        For example, if a zip entry is:
        
            ModName/LogicMods/Mod.pak
            
        then it is extracted as:
        
            {ITR2_Path}\IntoTheRadius2\Content\Paks\LogicMods\ModName\Mod.pak
            
      - If no recognized folder is found, the file is extracted to the Mods folder by default.
    """
    itr2_path = settings.get_ITR2_Path()
    if not itr2_path:
        messagebox.showerror("Error", "ITR2 path is not set in the configuration.")
        return
    
    base_dest = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks")
    mods_dest = os.path.join(base_dest, "Mods")
    logicmods_dest = os.path.join(base_dest, "LogicMods")
    luamods_dest = os.path.join(base_dest, "LuaMods")
    os.makedirs(mods_dest, exist_ok=True)
    os.makedirs(logicmods_dest, exist_ok=True)
    os.makedirs(luamods_dest, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            for member in z.namelist():
                if member.endswith("/"):
                    continue
                parts = member.split("/")
                # Default: use the entire member path.
                rel_path = os.path.join(*parts)
                # Determine target folder.
                target = "mods"  # default target
                if len(parts) >= 2:
                    # If the second part is a recognized mod type folder, remove it from the path.
                    if parts[1].lower() in ["mods", "logicmods", "luamods"]:
                        target = parts[1].lower()
                        # Rebuild relative path: preserve the first part (e.g. ModName) and then all remaining parts.
                        rel_path = os.path.join(parts[0], *parts[2:]) if len(parts) > 2 else parts[0]
                    else:
                        # Otherwise, if the first folder itself matches a target.
                        if parts[0].lower() in ["mods", "logicmods", "luamods"]:
                            target = parts[0].lower()
                # Set destination directory based on target.
                if target == "mods":
                    dest_dir = mods_dest
                elif target == "logicmods":
                    dest_dir = logicmods_dest
                elif target == "luamods":
                    dest_dir = luamods_dest
                else:
                    dest_dir = mods_dest
                
                final_dest = os.path.join(dest_dir, rel_path)
                os.makedirs(os.path.dirname(final_dest), exist_ok=True)
                with z.open(member) as source, open(final_dest, "wb") as target_file:
                    target_file.write(source.read())
        messagebox.showinfo("Installation Complete", "Mod installation completed successfully.")
    except Exception as e:
        messagebox.showerror("Installation Error", f"An error occurred during installation:\n{str(e)}")
