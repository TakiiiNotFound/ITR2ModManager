import os
import re
import zipfile
import io
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import xml.etree.ElementTree as ET
import settings

def open_fomod_install_window(parent):
    """
    Open a new, non‑resizable window (800x600) for Fomod mod installation.
    This window appears on top of the parent and starts the Fomod installer process.
    """
    fomod_win = ctk.CTkToplevel(parent)
    fomod_win.title("Fomod Install")
    fomod_win.geometry("800x600")
    fomod_win.resizable(False, False)
    fomod_win.transient(parent)
    fomod_win.grab_set()
    fomod_win.lift(parent)

    top_frame = ctk.CTkFrame(fomod_win)
    top_frame.pack(side="top", fill="x", padx=10, pady=10)

    title_label = ctk.CTkLabel(top_frame, text="Select the Fomod mod", font=("Arial", 16))
    title_label.pack(side="left", padx=10)

    select_button = ctk.CTkButton(top_frame, text="Select", command=lambda: select_zip_file(fomod_win))
    select_button.pack(side="left", padx=10)

    return fomod_win

def select_zip_file(fomod_win):
    """
    Open a file dialog to select a ZIP file. When a file is selected,
    parse ModuleConfig.xml and then show the install steps as separate pages.
    """
    file_path = filedialog.askopenfilename(
        title="Select Fomod Mod Zip File",
        filetypes=[("ZIP Files", "*.zip")]
    )
    if file_path:
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                modconfig_filename = next((f for f in z.namelist() if f.lower().endswith("moduleconfig.xml")), None)
                if not modconfig_filename:
                    messagebox.showerror("Error", "ModuleConfig.xml not found in the ZIP.", parent=fomod_win)
                    return
                modconfig_data = z.read(modconfig_filename)
                modconfig_root = ET.fromstring(modconfig_data)
                plugin_options = parse_moduleconfig(modconfig_root)
                # Use the paged UI rather than the single long list:
                show_fomod_choices_paged(fomod_win, file_path, plugin_options)
        except Exception as e:
            messagebox.showerror("Error", f"Could not process ZIP file: {e}", parent=fomod_win)

def parse_moduleconfig(root):
    """
    Parse ModuleConfig.xml and return a list of installStep dicts.
    Each dict has keys:
      'installStep': name,
      'plugins': list of plugin dicts with keys 'name', 'description', 'image_path', 'files'
              where 'files' is a list of dictionaries with keys 'source' and 'destination'
    """
    options = []
    install_steps = root.find("installSteps")
    if install_steps is not None:
        for instep in install_steps.findall("installStep"):
            step_name = instep.attrib.get("name", "InstallStep")
            plugins_list = []
            for opt_grp in instep.findall("optionalFileGroups"):
                for group in opt_grp.findall("group"):
                    plugins_el = group.find("plugins")
                    if plugins_el is not None:
                        for plugin in plugins_el.findall("plugin"):
                            p = {}
                            p["name"] = plugin.attrib.get("name", "Unnamed Plugin")
                            desc_el = plugin.find("description")
                            p["description"] = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
                            image_el = plugin.find("image")
                            p["image_path"] = image_el.attrib.get("path", "") if image_el is not None else ""
                            p["files"] = []
                            files_el = plugin.find("files")
                            if files_el is not None:
                                for folder_el in files_el.findall("folder"):
                                    src = folder_el.attrib.get("source", "")
                                    dest = folder_el.attrib.get("destination", "")
                                    p["files"].append({"source": src, "destination": dest})
                            plugins_list.append(p)
            if plugins_list:
                options.append({"installStep": step_name, "plugins": plugins_list})
    return options

def show_fomod_choices_paged(parent_window, zip_file_path, plugin_options):
    """
    Display the Fomod install options one installStep per page.
    Each page shows all plugins for that installStep (with image, name, description, and a checkbox, off by default).
    Navigation buttons "Back" and "Next" allow stepping between pages.
    On the final page, "Next" is replaced with "Install Selected".
    """
    choices_win = ctk.CTkToplevel(parent_window)
    choices_win.title("Fomod Install Options")
    choices_win.geometry("800x600")
    choices_win.resizable(False, False)
    choices_win.transient(parent_window)
    choices_win.grab_set()
    choices_win.lift(parent_window)

    # Create a main container for pages.
    main_container = ctk.CTkFrame(choices_win)
    main_container.pack(fill="both", expand=True, padx=10, pady=(10,50))  # leave space for nav buttons

    # Navigation frame for Back / Next buttons.
    nav_frame = ctk.CTkFrame(choices_win)
    nav_frame.pack(side="bottom", fill="x", padx=10, pady=10)
    
    # State: current page index.
    page_index = [0]  # Use list to allow mutable int.

    # Store the pages (each page is a frame) and the selections (each page: list of (plugin, BooleanVar)).
    pages = []
    selections = []

    def build_page(page_idx):
        # Clear main_container.
        for child in main_container.winfo_children():
            child.destroy()

        # Create a scrollable frame for the page.
        page_frame = ctk.CTkScrollableFrame(main_container)
        page_frame.pack(fill="both", expand=True)
        
        # Get installStep data for this page.
        step = plugin_options[page_idx]
        step_title = step["installStep"]
        title_label = ctk.CTkLabel(page_frame, text=step_title, font=("Arial", 16, "bold"))
        title_label.pack(fill="x", pady=(10, 5))
        
        # For each plugin in this installStep, display its details.
        page_selection = []  # List of tuples: (plugin, BooleanVar)
        for plugin in step["plugins"]:
            frame = ctk.CTkFrame(page_frame, border_width=1, border_color="#5e5e5e")
            frame.pack(fill="x", padx=10, pady=5)

            inner_frame = ctk.CTkFrame(frame)
            inner_frame.pack(fill="x", padx=5, pady=5)
            
            # Attempt to load the plugin image.
            img_label = None
            if plugin["image_path"]:
                try:
                    with zipfile.ZipFile(zip_file_path, 'r') as z:
                        image_file = next((f for f in z.namelist() 
                                           if f.lower().endswith(plugin["image_path"].lower())), None)
                        if image_file:
                            image_data = z.read(image_file)
                            from io import BytesIO
                            pil_image = Image.open(BytesIO(image_data))
                            pil_image = pil_image.resize((64, 64))
                            img = ctk.CTkImage(pil_image, size=(64, 64))
                            img_label = ctk.CTkLabel(inner_frame, image=img, text="")
                            img_label.image = img
                            img_label.pack(side="left", padx=5)
                except Exception as e:
                    print("Error loading plugin image:", e)
            if not img_label:
                placeholder = ctk.CTkLabel(inner_frame, text="[No Image]", width=64, height=64)
                placeholder.pack(side="left", padx=5)
            
            text_frame = ctk.CTkFrame(inner_frame)
            text_frame.pack(side="left", fill="both", expand=True, padx=5)
            
            name_label = ctk.CTkLabel(text_frame, text=plugin["name"], font=("Arial", 14))
            name_label.pack(anchor="w")
            desc_label = ctk.CTkLabel(text_frame, text=plugin["description"], font=("Arial", 10))
            desc_label.pack(anchor="w")
            
            # Create a checkbox that is off by default.
            var = ctk.BooleanVar(value=False)
            page_selection.append((plugin, var))
            checkbox = ctk.CTkCheckBox(frame, text="Select", variable=var)
            checkbox.pack(side="right", padx=5, pady=5)
        
        selections.append(page_selection)
        return page_frame

    # List to hold page frames. We'll build pages on demand.
    total_pages = len(plugin_options)
    
    def show_current_page():
        # Remove old page frame, if any, and build the current page.
        build_page(page_index[0])
        update_nav_buttons()

    def update_nav_buttons():
        # Clear nav_frame.
        for child in nav_frame.winfo_children():
            child.destroy()
        # Add Back button if not on first page.
        if page_index[0] > 0:
            back_btn = ctk.CTkButton(nav_frame, text="Back", command=go_back)
            back_btn.pack(side="left", padx=5)
        # On last page, show "Install Selected", else "Next".
        if page_index[0] < total_pages - 1:
            next_btn = ctk.CTkButton(nav_frame, text="Next", command=go_next)
            next_btn.pack(side="right", padx=5)
        else:
            install_btn = ctk.CTkButton(nav_frame, text="Install Selected", command=install_selected)
            install_btn.pack(side="right", padx=5)

    def go_next():
        if page_index[0] < total_pages - 1:
            page_index[0] += 1
            show_current_page()

    def go_back():
        if page_index[0] > 0:
            page_index[0] -= 1
            show_current_page()

    def install_selected():
        # Gather the selected plugins from all pages.
        all_selected = []
        for page in selections:
            for plugin, var in page:
                if var.get():
                    all_selected.append(plugin)
        if not all_selected:
            messagebox.showinfo("Fomod Install", "No plugins selected.", parent=choices_win)
            return
        # Proceed with installation (extraction process) for each selected plugin.
        itr2_path = settings.get_ITR2_Path()
        if not itr2_path:
            messagebox.showerror("Error", "ITR2 path is not set.", parent=choices_win)
            return
        base_dest = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks")
        for t in ["Mods", "LogicMods", "LuaMods"]:
            os.makedirs(os.path.join(base_dest, t), exist_ok=True)
        try:
            with zipfile.ZipFile(zip_file_path, "r") as z:
                for plugin in all_selected:
                    # For each file group in the plugin, extract matching files.
                    for file_group in plugin.get("files", []):
                        src = file_group.get("source", "").lower()
                        dest_rel = file_group.get("destination", "")
                        actual_dest = os.path.join(itr2_path, dest_rel)
                        os.makedirs(actual_dest, exist_ok=True)
                        pattern = src + "/"
                        for member in z.namelist():
                            if pattern in member.lower():
                                parts = member.split("/")
                                parts_lower = [p.lower() for p in parts]
                                if src in parts_lower:
                                    idx = parts_lower.index(src)
                                    subpath = "/".join(parts[idx+1:])
                                    if subpath:
                                        final_dest = os.path.join(actual_dest, subpath)
                                        os.makedirs(os.path.dirname(final_dest), exist_ok=True)
                                        with z.open(member) as s_file, open(final_dest, "wb") as t_file:
                                            t_file.write(s_file.read())
            messagebox.showinfo("Installation Complete", "Fomod mod installed successfully.", parent=choices_win)
        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n{e}", parent=choices_win)

    show_current_page()
    return choices_win
