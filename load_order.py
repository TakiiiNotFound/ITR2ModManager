import os
import re
import customtkinter as ctk
import settings

class NonInteractiveFolderItem(ctk.CTkFrame):
    def __init__(self, parent, path, indent=0, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.path = path
        self.indent = indent
        self.expanded = False
        self.fg = self.cget("fg_color")  # Use parent's foreground color
        
        folder_name = os.path.basename(path)
        self.has_children = self._check_has_children()
        
        # Header frame for this folder item.
        header = ctk.CTkFrame(self, fg_color=self.fg, height=25)
        header.pack(fill="x", padx=(self.indent, 0))
        
        if self.has_children:
            self.toggle_button = ctk.CTkButton(header, text="+", width=25, command=self.toggle, corner_radius=5)
            self.toggle_button.pack(side="left", padx=5)
        else:
            ctk.CTkLabel(header, text=" ", width=25).pack(side="left", padx=5)
        
        # Folder name label.
        self.label = ctk.CTkLabel(header, text=folder_name, anchor="w")
        self.label.pack(side="left", fill="x", expand=True)
        
        # For leaf folders, add an entry textbox on the right that accepts only 3 digits.
        if not self.has_children:
            self.entry_var = ctk.StringVar(value="")
            self.entry_var.trace_add("write", self.validate_entry)
            self.value_entry = ctk.CTkEntry(header, textvariable=self.entry_var, width=50, justify="center")
            self.value_entry.pack(side="right", padx=5)
            
        self.children_frame = None

    def validate_entry(self, *args):
        value = self.entry_var.get()
        new_value = ''.join(filter(str.isdigit, value))[:3]
        if new_value != value:
            self.entry_var.set(new_value)

    def _check_has_children(self):
        try:
            items = os.listdir(self.path)
        except Exception:
            items = []
        subdirs = [d for d in items if os.path.isdir(os.path.join(self.path, d))]
        return len(subdirs) > 0

    def toggle(self):
        if self.expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.expanded = True
        if hasattr(self, "toggle_button"):
            self.toggle_button.configure(text="-")
        if self.children_frame is None:
            self.children_frame = ctk.CTkFrame(self, fg_color=self.fg)
            self.children_frame.pack(fill="x", padx=(20, 0))
            self._populate_children()
        else:
            self.children_frame.pack(fill="x", padx=(20, 0))

    def collapse(self):
        self.expanded = False
        if hasattr(self, "toggle_button"):
            self.toggle_button.configure(text="+")
        if self.children_frame:
            self.children_frame.pack_forget()

    def _populate_children(self):
        try:
            items = os.listdir(self.path)
        except Exception:
            items = []
        subdirs = sorted(
            [os.path.join(self.path, d) for d in items if os.path.isdir(os.path.join(self.path, d))],
            key=lambda x: os.path.basename(x).lower()
        )
        for sub in subdirs:
            child = NonInteractiveFolderItem(self.children_frame, sub, indent=self.indent + 20)
            child.pack(fill="x", pady=1)

def build_collapsible_tree(parent, path):
    """
    Build a collapsible tree view showing only the immediate subfolders (and their subfolders recursively)
    of the provided path. The root folder itself is not shown.
    """
    if not path or not os.path.isdir(path):
        ctk.CTkLabel(parent, text="Folder not found").pack(pady=20)
        return
    try:
        items = os.listdir(path)
    except Exception:
        items = []
    folders = sorted(
        [os.path.join(path, d) for d in items if os.path.isdir(os.path.join(path, d))],
        key=lambda x: os.path.basename(x).lower()
    )
    if not folders:
        ctk.CTkLabel(parent, text="No folders found").pack(pady=20)
    else:
        for folder in folders:
            item = NonInteractiveFolderItem(parent, folder, indent=0)
            item.pack(fill="x", pady=2)

# --------------------------
# File-renaming functions
# --------------------------

def pad_number(num_str):
    """Return the number string padded to 3 digits (e.g., '1' becomes '001')."""
    return num_str.zfill(3)

def rename_files_in_folder(folder_path, number):
    """
    Rename files in folder_path that have the extensions .pak, .ucas, or .utoc.
    The new format is: <padded>_<original_filename> where the original filename is cleaned
    of any existing 3-digit prefix and underscore.
    
    For example, "Mod.pak" becomes "123_Mod.pak" if the entered number is 123.
    """
    import re
    for item in os.listdir(folder_path):
        full_item = os.path.join(folder_path, item)
        if os.path.isfile(full_item):
            for ext in [".pak", ".ucas", ".utoc"]:
                if item.endswith(ext) and not item.endswith(ext + ".off"):
                    # Remove a leading three-digit prefix and underscore if it exists.
                    base_clean = re.sub(r"^\d{3}_", "", item)
                    new_name = f"{number}_{base_clean}"
                    os.rename(full_item, os.path.join(folder_path, new_name))
                    break

def remove_prefix_in_folder(folder_path):
    """
    Remove a leading 3-digit prefix and underscore from files in folder_path.
    """
    import re
    for item in os.listdir(folder_path):
        full_item = os.path.join(folder_path, item)
        if os.path.isfile(full_item):
            new_name = re.sub(r"^\d{3}_", "", item)
            os.rename(full_item, os.path.join(folder_path, new_name))

def process_tree(widget):
    """
    Recursively traverse widget's children and return a list of all NonInteractiveFolderItem
    instances that are leaf nodes (i.e. have an associated entry widget).
    """
    items = []
    if isinstance(widget, NonInteractiveFolderItem) and hasattr(widget, "entry_var"):
        items.append(widget)
    for child in widget.winfo_children():
        items.extend(process_tree(child))
    return items

def reset_entries(widget):
    """
    Recursively traverse widget's children and clear the entry value of all NonInteractiveFolderItem
    instances that have an entry widget.
    """
    if isinstance(widget, NonInteractiveFolderItem) and hasattr(widget, "entry_var"):
        widget.entry_var.set("")
    for child in widget.winfo_children():
        reset_entries(child)

# --------------------------
# Load Order Window
# --------------------------
def open_load_order_window(parent):
    """
    Open a new, non-resizable load order window (800x600) that contains a CTkTabview with two tabs:
      - "Mods": displays a collapsible, scrollable folder tree from {ITR2_Path}\IntoTheRadius2\Content\Paks\Mods
      - "LogicMods": displays a collapsible, scrollable folder tree from {ITR2_Path}\IntoTheRadius2\Content\Paks\LogicMods
    Two buttons ("Apply" and "Reset") are added at the top.
    """
    load_order_window = ctk.CTkToplevel(parent)
    load_order_window.title("Load Order")
    width, height = 800, 600
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    load_order_window.geometry(f"{width}x{height}+{x}+{y}")
    load_order_window.resizable(False, False)
    load_order_window.transient(parent)
    load_order_window.grab_set()
    load_order_window.lift(parent)
    
    # Button frame at the top, matching the window's background.
    button_frame = ctk.CTkFrame(load_order_window, fg_color=load_order_window.cget("fg_color"), corner_radius=0)
    button_frame.pack(fill="x", pady=5, padx=10)
    
    def apply_load_order():
        print("Apply clicked")
        # Process each leaf folder (NonInteractiveFolderItem with an entry).
        for scroll in (mods_scroll, logicmods_scroll):
            for item in process_tree(scroll):
                num_val = item.entry_var.get().strip()
                if num_val:
                    padded = pad_number(num_val)
                    rename_files_in_folder(item.path, padded)
                else:
                    remove_prefix_in_folder(item.path)
    
    def reset_load_order():
        print("Reset clicked")
        reset_entries(mods_scroll)
        reset_entries(logicmods_scroll)
    
    apply_button = ctk.CTkButton(button_frame, text="Apply", command=apply_load_order)
    apply_button.pack(side="left", padx=5)
    
    reset_button = ctk.CTkButton(button_frame, text="Reset", command=reset_load_order)
    reset_button.pack(side="left", padx=5)
    
    tabview = ctk.CTkTabview(load_order_window, width=780, height=500)
    tabview.pack(padx=10, pady=10, fill="both", expand=True)
    tabview.add("Mods")
    tabview.add("LogicMods")
    
    itr2_path = settings.get_ITR2_Path()
    
    # Build tree for Mods tab.
    mods_tab = tabview.tab("Mods")
    if itr2_path:
        mods_path = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods")
        if os.path.isdir(mods_path):
            mods_scroll = ctk.CTkScrollableFrame(mods_tab)
            mods_scroll.pack(fill="both", expand=True)
            build_collapsible_tree(mods_scroll, mods_path)
        else:
            ctk.CTkLabel(mods_tab, text="Mods folder not found").pack(pady=20)
    else:
        ctk.CTkLabel(mods_tab, text="ITR2 path not set").pack(pady=20)
    
    # Build tree for LogicMods tab.
    logicmods_tab = tabview.tab("LogicMods")
    if itr2_path:
        logicmods_path = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "LogicMods")
        if os.path.isdir(logicmods_path):
            logicmods_scroll = ctk.CTkScrollableFrame(logicmods_tab)
            logicmods_scroll.pack(fill="both", expand=True)
            build_collapsible_tree(logicmods_scroll, logicmods_path)
        else:
            ctk.CTkLabel(logicmods_tab, text="LogicMods folder not found").pack(pady=20)
    else:
        ctk.CTkLabel(logicmods_tab, text="ITR2 path not set").pack(pady=20)
    
    return load_order_window
