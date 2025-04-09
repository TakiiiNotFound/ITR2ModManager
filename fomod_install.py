import os
import shutil
import zipfile
import tempfile
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import config

def get_master():
    # Reuse existing Tk root if available; otherwise create one.
    if tk._default_root is None:
        root = tk.Tk()
        root.withdraw()
        # Set the window icon for the root.
        appdata = os.getenv("APPDATA")
        icon_path = os.path.join(appdata, "ITR2ModManager", "ITR2MM.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except Exception as e:
                print("Error setting icon on root:", e)
        return root, True
    else:
        return tk._default_root, False

def select_archive(master=None):
    if master is None:
        master, _ = get_master()
    result = filedialog.askopenfilename(
        master=master,
        title="Select mod archive (.zip, .rar, .7z)",
        filetypes=[("Zip files", "*.zip"), ("RAR files", "*.rar"), ("7z files", "*.7z")]
    )
    return result

def extract_archive(archive_path, extract_to):
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Failed to extract archive:\n{str(e)}", parent=archive_path)
        return False

def find_fomod_folder(extracted_path):
    for root_dir, dirs, files in os.walk(extracted_path):
        for d in dirs:
            if d.lower() == "fomod":
                return os.path.join(root_dir, d)
    return None

def parse_info_xml(info_xml_path):
    try:
        tree = ET.parse(info_xml_path)
        root = tree.getroot()
        mod_title = root.findtext("Name", default="")
        mod_description = root.findtext("Description", default="")
        return mod_title, mod_description
    except Exception as e:
        messagebox.showerror("XML Parse Error", f"Failed to parse info.xml:\n{str(e)}", parent=info_xml_path)
        return "", ""

def parse_module_config(module_config_path):
    install_steps = []
    try:
        tree = ET.parse(module_config_path)
        root = tree.getroot()
        for step in root.findall(".//installStep"):
            step_name = step.attrib.get("name", "Unnamed Step")
            plugins = []
            for plugin in step.findall(".//plugin"):
                title = plugin.attrib.get("name", "Unnamed")
                description = plugin.findtext("description", default="")
                image_elem = plugin.find("image")
                image = image_elem.attrib.get("path") if image_elem is not None else ""
                folders = []
                files_elem = plugin.find("files")
                if files_elem is not None:
                    for folder_elem in files_elem.findall("folder"):
                        source = folder_elem.attrib.get("source", "")
                        if source:
                            folders.append(source)
                plugins.append({
                    "Title": title,
                    "Description": description,
                    "Image": image,
                    "Folders": folders
                })
            install_steps.append({
                "name": step_name,
                "plugins": plugins
            })
        return install_steps
    except Exception as e:
        messagebox.showerror("XML Parse Error", f"Failed to parse ModuleConfig.xml:\n{str(e)}", parent=module_config_path)
        return []

def run_install_steps_wizard(install_steps, master, image_base):
    results = {}
    current_step = 0

    wizard = tk.Toplevel(master)
    wizard.title("Fomod Install Wizard")
    wizard.configure(bg="#171717")
    # Set the wizard window's icon
    appdata = os.getenv("APPDATA")
    icon_path = os.path.join(appdata, "ITR2ModManager", "ITR2MM.ico")
    if os.path.exists(icon_path):
        try:
            wizard.iconbitmap(icon_path)
        except Exception as e:
            print("Error setting wizard icon:", e)

    # Main frame holds two subframes: left (options) and right (image display)
    main_frame = tk.Frame(wizard, bg="#171717")
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)
    
    # Left frame: a canvas with a vertical scrollbar (using tk.Scrollbar)
    left_frame = tk.Frame(main_frame, bg="#171717")
    left_frame.pack(side="left", fill="both", expand=True)
    canvas = tk.Canvas(left_frame, bg="#171717", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    content_frame = tk.Frame(canvas, bg="#171717")
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    content_frame.bind("<Configure>", on_configure)
    
    # Right frame: image display area.
    image_frame = tk.Frame(main_frame, bg="#171717")
    image_frame.pack(side="right", fill="both", expand=True)
    image_label = tk.Label(image_frame, bg="#171717")
    image_label.pack(padx=5, pady=5)
    
    var_dict = {}
    
    def show_image(plugin, var):
        if var.get() == 1 and plugin["Image"]:
            image_path = os.path.join(image_base, plugin["Image"])
            if not os.path.exists(image_path):
                messagebox.showerror("Image Error", f"Image file not found:\n{image_path}", parent=wizard)
                return
            try:
                img = Image.open(image_path)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                image_label.config(image=img_tk)
                image_label.image = img_tk
            except Exception as e:
                messagebox.showerror("Image Error", f"Failed to load image:\n{str(e)}", parent=wizard)
        else:
            image_label.config(image='')
            image_label.image = None
    
    def load_step(index):
        nonlocal var_dict
        for widget in content_frame.winfo_children():
            widget.destroy()
        var_dict = {}
        if index >= len(install_steps):
            wizard.destroy()
            return
        step = install_steps[index]
        header = tk.Label(content_frame, text=f"Options for '{step['name']}':", fg="white", bg="#171717", font=("TkDefaultFont", 10, "bold"))
        header.pack(anchor="w", padx=5, pady=5)
        for plugin in step["plugins"]:
            frame = tk.Frame(content_frame, bg="#171717")
            frame.pack(anchor="w", padx=5, pady=2, fill="x")
            var = tk.IntVar(value=0)
            var_dict[plugin["Title"]] = var
            var.trace_add("write", lambda *args, p=plugin, v=var: show_image(p, v))
            title_label = tk.Label(frame, text=plugin["Title"], fg="white", bg="#171717", font=("TkDefaultFont", 10, "bold"))
            title_label.pack(side="top", anchor="w")
            desc_label = tk.Label(frame, text=plugin["Description"], fg="white", bg="#171717", wraplength=300, justify="left")
            desc_label.pack(side="top", anchor="w")
            if plugin["Image"]:
                image_text = f"Image: {plugin['Image']}"
                image_label_plugin = tk.Label(frame, text=image_text, fg="white", bg="#171717")
                image_label_plugin.pack(side="top", anchor="w")
            checkbox = tk.Checkbutton(frame, variable=var, bg="#171717", fg="white", activebackground="#171717", selectcolor="#171717")
            checkbox.pack(side="right", anchor="e")
        next_btn = tk.Button(content_frame, text="Next", command=next_step)
        next_btn.pack(pady=10)
        canvas.yview_moveto(0)
    
    def next_step():
        nonlocal current_step
        step = install_steps[current_step]
        selected = [title for title, var in var_dict.items() if var.get() == 1]
        results[step["name"]] = selected
        current_step += 1
        if current_step < len(install_steps):
            load_step(current_step)
        else:
            wizard.destroy()
    
    load_step(current_step)
    wizard.grab_set()
    wizard.wait_window()
    return results

def add_module_files(install_folder):
    for current_dir, dirs, files in os.walk(install_folder):
        if os.path.abspath(current_dir) == os.path.abspath(install_folder):
            continue
        if "module" not in files:
            module_file = os.path.join(current_dir, "module")
            try:
                with open(module_file, "w") as f:
                    pass
            except Exception:
                pass

def perform_fomod_install(extracted_path, install_folder, install_steps, selections):
    try:
        for step in install_steps:
            selected_titles = selections.get(step["name"], [])
            for plugin in step["plugins"]:
                if plugin["Title"] in selected_titles:
                    for folder_source in plugin["Folders"]:
                        source_path = os.path.join(extracted_path, folder_source)
                        if os.path.exists(source_path):
                            target_path = os.path.join(install_folder, os.path.basename(folder_source))
                            if os.path.exists(target_path):
                                shutil.rmtree(target_path)
                            shutil.copytree(source_path, target_path)
                        else:
                            messagebox.showerror("Error", f"Required folder '{folder_source}' not found in the archive.", parent=install_folder)
                            return False
        add_module_files(install_folder)
        return True
    except Exception as e:
        messagebox.showerror("Install Error", f"Error during installation:\n{str(e)}", parent=install_folder)
        return False

def fomod_install():
    master, created = get_master()
    archive_path = select_archive(master=master)
    if not archive_path:
        if created: master.destroy()
        return

    temp_dir = tempfile.mkdtemp(prefix="fomod_")
    if not extract_archive(archive_path, temp_dir):
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    fomod_folder = None
    for r, d, f in os.walk(temp_dir):
        for folder in d:
            if folder.lower() == "fomod":
                fomod_folder = os.path.join(r, folder)
                break
        if fomod_folder:
            break

    if not fomod_folder:
        messagebox.showerror("Error", "No 'fomod' folder found in the archive.", parent=master)
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    info_xml_path = os.path.join(fomod_folder, "info.xml")
    module_config_path = os.path.join(fomod_folder, "ModuleConfig.xml")
    if not os.path.exists(info_xml_path) or not os.path.exists(module_config_path):
        messagebox.showerror("Error", "info.xml and/or ModuleConfig.xml not found in the fomod folder.", parent=master)
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    default_mod_title, _ = parse_info_xml(info_xml_path)
    install_steps = parse_module_config(module_config_path)
    if not install_steps:
        messagebox.showerror("Error", "No install steps found in ModuleConfig.xml.", parent=master)
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    selections = run_install_steps_wizard(install_steps, master=master, image_base=temp_dir)
    
    mod_name = simpledialog.askstring("Mod Name", "Enter mod name:", initialvalue=default_mod_title, parent=master)
    if not mod_name:
        messagebox.showerror("Error", "No mod name provided.", parent=master)
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    cfg = config.load_config()
    itr2_path = cfg.get("itr2_path")
    if not itr2_path or not os.path.exists(itr2_path):
        messagebox.showerror("Error", "ITR2 path is not configured correctly.", parent=master)
        shutil.rmtree(temp_dir)
        if created: master.destroy()
        return

    mod_install_folder = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods", mod_name)
    os.makedirs(mod_install_folder, exist_ok=True)

    if perform_fomod_install(temp_dir, mod_install_folder, install_steps, selections):
        fomod_marker = os.path.join(mod_install_folder, "fomod")
        with open(fomod_marker, "w") as f:
            f.write("")
        messagebox.showinfo("Success", "Fomod mod installed successfully.", parent=master)
    else:
        messagebox.showerror("Error", "An error occurred during Fomod installation.", parent=master)

    shutil.rmtree(temp_dir)
    if created: master.destroy()

if __name__ == "__main__":
    fomod_install()
