import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import config

def get_default_order_from_folder(folder):
    """
    Scans the given folder for files ending with '.pak'.
    If a file is found that starts with three digits followed by an underscore,
    returns that numeric prefix (e.g. "727" from "727_ModFile.pak").
    Otherwise, returns an empty string.
    """
    if not os.path.isdir(folder):
        return ""
    for file in os.listdir(folder):
        if file.lower().endswith(".pak"):
            m = re.match(r'^(\d{3})_', file)
            if m:
                return m.group(1)
    return ""

def rename_files_in_folder(folder, order):
    """
    Recursively renames files in 'folder' with extensions: .pak, .utoc, or .ucas.
    
    If 'order' is non-empty:
      - Any existing three-digit underscore prefix is replaced with the new order (padded to 3 digits)
        or prepended if not present.
    If 'order' is empty:
      - Any existing three-digit underscore prefix is removed.
    """
    valid_exts = (".pak", ".utoc", ".ucas")
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.lower().endswith(valid_exts):
                if order:
                    formatted_order = order.zfill(3)
                    m = re.match(r'^(\d{3})_(.*)$', filename)
                    if m:
                        new_filename = f"{formatted_order}_{m.group(2)}"
                    else:
                        new_filename = f"{formatted_order}_{filename}"
                else:
                    new_filename = re.sub(r'^\d{3}_', '', filename)
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_filename)
                if old_path != new_path:
                    try:
                        os.rename(old_path, new_path)
                    except Exception as e:
                        messagebox.showerror("Rename Error", f"Error renaming {old_path}:\n{str(e)}")

def scan_mods_folder(mods_dir):
    """
    Scans the given mods directory for mod items.
    - Each mod is a subdirectory of mods_dir.
    - If a mod folder contains an "off" file, it is skipped.
    - If a mod folder contains a file named "fomod", it is considered a fomod mod;
      its subdirectories (modules) are added as children unless they contain an "off" file.
    Returns a list of dictionaries with keys: name, path, type, and children.
    """
    items = []
    if not os.path.exists(mods_dir):
        messagebox.showerror("Error", f"Mods folder not found:\n{mods_dir}")
        return items
    for item in os.listdir(mods_dir):
        full_path = os.path.join(mods_dir, item)
        if os.path.isdir(full_path):
            off_file = os.path.join(full_path, "off")
            if os.path.exists(off_file):
                continue
            mod_type = "mod"
            fomod_marker = os.path.join(full_path, "fomod")
            if os.path.exists(fomod_marker):
                mod_type = "fomod"
            children = []
            if mod_type == "fomod":
                for child in os.listdir(full_path):
                    child_path = os.path.join(full_path, child)
                    if os.path.isdir(child_path):
                        off_child = os.path.join(child_path, "off")
                        if os.path.exists(off_child):
                            continue
                        children.append({"name": child, "path": child_path})
            items.append({"name": item, "path": full_path, "type": mod_type, "children": children})
    return items

def get_mod_dict():
    """
    Scans the mods folder (using the ITR2 path from config) and builds a dictionary:
      - Top-level mods: key is mod name, value is the mod dictionary.
      - For modules: key is "ParentName::ChildName", value is the child dictionary.
    """
    cfg = config.load_config()
    itr2_path = cfg.get("itr2_path", "")
    mods_dir = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods")
    mods_list = scan_mods_folder(mods_dir)
    mod_dict = {}
    for mod in mods_list:
        mod_dict[mod["name"]] = mod
        if mod.get("children"):
            for child in mod["children"]:
                mod_dict[f"{mod['name']}::{child['name']}"] = child
    return mod_dict

def open_load_order_window(master=None):
    """
    Opens a "Change Load Order" window displaying a Treeview with all mod items
    (and their child modules) plus an "Order" column for inline editing.
    
    - Each mod (or module) gets a default order by scanning its folder for .pak files.
    - Items with an "off" file are excluded.
    - Inline editing for the "Order" cell allows only up to 3 digits; if empty,
      any existing prefix is removed.
    - For items whose Type is "fomod", editing is disallowed.
    - The top frame includes an "Apply" button (which opens a confirmation popup with Yes/No) and a "Reset" button.
    """
    if master is None:
        master = tk.Tk()
        master.withdraw()

    window = tk.Toplevel(master)
    window.title("Change Load Order")
    window.geometry("500x400")
    window.configure(bg="#171717")
    
    # Set the window icon using ITR2MM.ico from %APPDATA%\ITR2ModManager
    appdata = os.getenv("APPDATA")
    icon_path = os.path.join(appdata, "ITR2ModManager", "ITR2MM.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception as e:
            print("Error setting load_order window icon:", e)
    
    # Top frame for Apply and Reset buttons.
    top_frame = tk.Frame(window, bg="#171717")
    top_frame.pack(fill="x", padx=10, pady=5)
    
    def apply_order():
        order_dict = {}
        for top_id in tree.get_children():
            mod_name = tree.item(top_id, "text")
            order_val = tree.set(top_id, "Order").strip()
            if order_val:
                order_val = order_val.zfill(3)
            order_dict[mod_name] = order_val
            for sub_id in tree.get_children(top_id):
                sub_name = tree.item(sub_id, "text")
                sub_order = tree.set(sub_id, "Order").strip()
                if sub_order:
                    sub_order = sub_order.zfill(3)
                order_dict[f"{mod_name}::{sub_name}"] = sub_order
        
        # Confirmation popup.
        confirm = messagebox.askyesno("Confirm", "apply the order ??", parent=window)
        if not confirm:
            return

        mod_dict = get_mod_dict()
        for key, ord_val in order_dict.items():
            if key in mod_dict:
                folder = mod_dict[key]["path"]
                rename_files_in_folder(folder, ord_val)
        print("Applied load order:", order_dict)
        messagebox.showinfo("Apply", "Load order applied and files renamed!", parent=window)
    
    def reset_order():
        # Clear all Order values (without popup).
        for top_id in tree.get_children():
            tree.set(top_id, "Order", "")
            for sub_id in tree.get_children(top_id):
                tree.set(sub_id, "Order", "")
        # No popup here.
    
    apply_btn = tk.Button(top_frame, text="Apply", command=apply_order)
    apply_btn.pack(side="left", padx=(0, 5))
    reset_btn = tk.Button(top_frame, text="Reset", command=reset_order)
    reset_btn.pack(side="left", padx=(5, 0))
    
    # Create the Treeview with additional columns: Type and Order.
    tree = ttk.Treeview(window, columns=("Type", "Order"), show="tree headings")
    tree.heading("#0", text="Mod Name")
    tree.heading("Type", text="Type")
    tree.heading("Order", text="Order")
    tree.column("Order", width=80, anchor="center")
    tree.tag_configure("fomod", foreground="blue")
    tree.tag_configure("module", foreground="lightblue")
    tree.pack(fill="both", expand=True, padx=10, pady=5)
    
    def insert_item(item, parent=""):
        default_order = get_default_order_from_folder(item["path"])
        tag = item["type"] if item["type"] == "fomod" else ""
        item_id = tree.insert(parent, "end", text=item["name"],
                              values=(item["type"], default_order), tags=(tag,))
        if item["type"] == "fomod":
            for child in item.get("children", []):
                child_default = get_default_order_from_folder(child["path"])
                tree.insert(item_id, "end", text=child["name"],
                            values=("module", child_default), tags=("module",))
    
    def load_tree_items():
        cfg = config.load_config()
        itr2_path = cfg.get("itr2_path", "")
        mods_dir = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods")
        mods_list = scan_mods_folder(mods_dir)
        for mod in mods_list:
            insert_item(mod)
    
    load_tree_items()
    
    # Inline editing for the "Order" column.
    def on_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = tree.identify_column(event.x)
        # "#0": Mod Name, "#1": Type, "#2": Order.
        if col != "#2":
            return
        rowid = tree.identify_row(event.y)
        if not rowid:
            return
        item_type = tree.set(rowid, "Type")
        if item_type.lower() == "fomod":
            messagebox.showinfo("Info", "Ordering is not allowed for fomod items.", parent=window)
            return
        x, y, width, height = tree.bbox(rowid, "Order")
        entry = tk.Entry(tree, justify="center")
        def validate_input(P):
            return (P.isdigit() or P == "") and len(P) <= 3
        vcmd = (tree.register(validate_input), '%P')
        entry.config(validate="key", validatecommand=vcmd)
        current_val = tree.set(rowid, "Order")
        entry.insert(0, current_val)
        entry.select_range(0, tk.END)
        entry.focus()
        def on_entry_confirm(event):
            new_val = entry.get()
            tree.set(rowid, "Order", new_val)
            entry.destroy()
        entry.bind("<Return>", on_entry_confirm)
        entry.bind("<FocusOut>", lambda event: entry.destroy())
        entry.place(x=x, y=y, width=width, height=height)
    
    tree.bind("<Double-1>", on_double_click)
    
    window.mainloop()

if __name__ == "__main__":
    open_load_order_window()
