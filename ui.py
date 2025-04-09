import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import webbrowser
import config
from settings import (
    select_itr2_folder,
    select_temp_folder,
    clear_temp_folder,
    open_fomod_folder,
    check_itr2_game_folder
)
import help as help_logic  # Contains support functions for Help tab links
from mods import populate_mods_tree, toggle_mod_state, delete_mod, mod_items
import basic_install    # For Basic mod install
import fomod_install    # For Fomod mod install
import load_order       # For Load Order window

def get_expanded_paths(tree):
    """Collects the set of folder paths for items that are currently expanded."""
    expanded = set()
    def rec(item_id):
        if tree.item(item_id, "open"):
            mod = mod_items.get(item_id)
            if mod:
                expanded.add(mod["path"])
            for child in tree.get_children(item_id):
                rec(child)
    for item in tree.get_children():
        rec(item)
    return expanded

def start_ui():
    # Load configuration at startup
    cfg = config.load_config()
    itr2_path = cfg.get("itr2_path", "")
    temp_path = cfg.get("temp_path", "")
    display_itr2 = itr2_path.replace("\\", "/")
    display_temp = temp_path.replace("\\", "/")

    root = tk.Tk()
    root.title("ITR2 Mod Manager")
    root.geometry("800x600")
    root.configure(bg="#171717")
    root.resizable(False, False)
    
    # Set window icon from %APPDATA%\ITR2ModManager\ITR2MM.ico
    appdata = os.getenv("APPDATA")
    icon_path = os.path.join(appdata, "ITR2ModManager", "ITR2MM.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception as e:
            print("Error setting icon:", e)
    
    # Set up ttk style for the Treeview (Mods list) background and field background to #282828.
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#282828", fieldbackground="#282828", foreground="white")

    # Top frame for header and buttons
    top_frame = tk.Frame(root, bg="#171717")
    top_frame.pack(side="top", fill="x", padx=20, pady=10)
    
    # "Launch ITR2" button on the left
    launch_itr2_btn = tk.Button(top_frame, text="Launch ITR2", 
                                command=lambda: webbrowser.open("steam://rungameid/2307350"))
    launch_itr2_btn.pack(side="left", anchor="w", padx=(0, 10))
    
    header_label = tk.Label(top_frame, text="ITR2 Mod Manager", font=("TkDefaultFont", 16, "bold"), fg="white", bg="#171717")
    header_label.pack(side="left", anchor="w")
    
    def open_new_mods_url():
        webbrowser.open("https://www.nexusmods.com/games/intotheradius2/mods")
    find_mods_button = tk.Button(top_frame, text="Find new mods", command=open_new_mods_url)
    find_mods_button.pack(side="right", anchor="e")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both", padx=20, pady=20)

    # Define tabs: Mods, Install, Settings, Help, UE4SS soon...
    tab_names = ["Mods", "Install", "Settings", "Help", "UE4SS soon..."]
    tabs = {}
    for name in tab_names:
        frame = tk.Frame(notebook, bg="#171717")
        notebook.add(frame, text=name)
        tabs[name] = frame
    # Disable UE4SS tab (index 4)
    notebook.tab(4, state="disabled")

    # ---------------- Mods Tab ----------------
    mods_frame = tabs["Mods"]
    mods_tree = ttk.Treeview(mods_frame, columns=("toggle", "delete"), show="tree headings")
    mods_tree.heading("#0", text="Mod")
    mods_tree.heading("toggle", text="is enable?")
    mods_tree.heading("delete", text="Delete")
    mods_tree.column("toggle", width=100, anchor="center")
    mods_tree.column("delete", width=100, anchor="center")
    mods_tree.pack(expand=True, fill="both", padx=20, pady=20)
    mods_tree.tag_configure("unknown", foreground="red")
    populate_mods_tree(mods_tree)

    def on_tree_click(event):
        region = mods_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = mods_tree.identify_column(event.x)
        item_id = mods_tree.identify_row(event.y)
        if not item_id:
            return
        mod_item = mod_items.get(item_id)
        if not mod_item:
            return
        expanded = get_expanded_paths(mods_tree)
        if column == "#1":
            if mod_item.get("type") == "fomod":
                return
            if mod_item.get("type") != "unknown":
                toggle_mod_state(mod_item)
            populate_mods_tree(mods_tree, expanded)
        elif column == "#2":
            answer = messagebox.askyesno("Delete Mod", "Are you sure to delete this mod?")
            if answer:
                if delete_mod(mod_item):
                    populate_mods_tree(mods_tree, expanded)
                else:
                    messagebox.showerror("Error", "Failed to delete mod.")
    mods_tree.bind("<Button-1>", on_tree_click)

    # ---------------- Install Tab ----------------
    install_frame = tabs["Install"]
    # Basic mod install
    basic_label = tk.Label(install_frame, text="Basic mod install", font=("TkDefaultFont", 12, "bold"), fg="white", bg="#171717")
    basic_label.pack(side="top", anchor="w", padx=20, pady=(20, 5))
    basic_install_button = tk.Button(install_frame, text="install", command=basic_install.basic_install)
    basic_install_button.pack(side="top", anchor="w", padx=20, pady=5)
    # Fomod mod install
    fomod_label = tk.Label(install_frame, text="Fomod mod install", font=("TkDefaultFont", 12, "bold"), fg="white", bg="#171717")
    fomod_label.pack(side="top", anchor="w", padx=20, pady=(20, 5))
    fomod_install_button = tk.Button(install_frame, text="install", command=fomod_install.fomod_install)
    fomod_install_button.pack(side="top", anchor="w", padx=20, pady=5)

    # ---------------- Settings Tab ----------------
    settings_frame = tabs["Settings"]
    game_folder_frame = tk.Frame(settings_frame, bg="#171717")
    game_folder_frame.pack(side="top", anchor="nw", padx=20, pady=10)
    game_folder_label = tk.Label(game_folder_frame, text="ITR2 Game folder", fg="white", bg="#171717")
    game_folder_label.grid(row=0, column=0, sticky="w", columnspan=3)
    game_folder_entry = tk.Entry(game_folder_frame, width=50)
    game_folder_entry.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
    game_folder_entry.insert(0, display_itr2)
    def on_select_itr2():
        folder = select_itr2_folder()
        if folder:
            display_folder = folder.replace("\\", "/")
            game_folder_entry.delete(0, tk.END)
            game_folder_entry.insert(0, display_folder)
    game_folder_select = tk.Button(game_folder_frame, text="Select", command=on_select_itr2)
    game_folder_select.grid(row=1, column=1, padx=5, pady=5)
    def on_check_itr2():
        folder = game_folder_entry.get()
        check_itr2_game_folder(folder)
    game_folder_check = tk.Button(game_folder_frame, text="Check", command=on_check_itr2)
    game_folder_check.grid(row=1, column=2, padx=5, pady=5)
    
    temp_folder_frame = tk.Frame(settings_frame, bg="#171717")
    temp_folder_frame.pack(side="top", anchor="nw", padx=20, pady=10)
    temp_folder_label = tk.Label(temp_folder_frame, text="Temp folder", fg="white", bg="#171717")
    temp_folder_label.grid(row=0, column=0, sticky="w", columnspan=2)
    temp_folder_entry = tk.Entry(temp_folder_frame, width=50)
    temp_folder_entry.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
    temp_folder_entry.insert(0, display_temp)
    def on_select_temp():
        folder = select_temp_folder()
        if folder:
            display_folder = folder.replace("\\", "/")
            temp_folder_entry.delete(0, tk.END)
            temp_folder_entry.insert(0, display_folder)
    temp_folder_select = tk.Button(temp_folder_frame, text="Select", command=on_select_temp)
    temp_folder_select.grid(row=1, column=1, padx=5, pady=5, sticky="e")
    
    buttons_frame = tk.Frame(settings_frame, bg="#171717")
    buttons_frame.pack(side="top", anchor="nw", padx=20, pady=10)
    def on_clear_temp():
        clear_temp_folder()
    clear_temp_button = tk.Button(buttons_frame, text="Clear temp", command=on_clear_temp)
    clear_temp_button.grid(row=0, column=0, padx=(0, 10), pady=5)
    
    # New: Change load order button under Clear temp.
    change_load_order_btn = tk.Button(buttons_frame, text="Change load order", 
                                      command=lambda: load_order.open_load_order_window(master=root))
    change_load_order_btn.grid(row=0, column=1, padx=(10, 0), pady=5)
    
    def on_open_fomod():
        open_fomod_folder()
    open_fomod_button = tk.Button(buttons_frame, text="Open Fomod Creation Tool folder", command=on_open_fomod)
    open_fomod_button.grid(row=0, column=2, padx=(10, 0), pady=5)

    # ---------------- Help Tab ----------------
    help_frame = tabs["Help"]
    help_fomod_label = tk.Label(help_frame, text="Fomod setup tutorial soon...", fg="white", bg="#171717")
    help_fomod_label.pack(side="top", anchor="nw", padx=20, pady=(20, 5))
    tutorial_button = tk.Button(help_frame, text="Tutorial")  # No command assigned.
    tutorial_button.pack(side="top", anchor="nw", padx=20, pady=5)
    
    github_label = tk.Label(help_frame, text="ITR2 Mod Manager Github page", fg="white", bg="#171717")
    github_label.pack(side="top", anchor="nw", padx=20, pady=(20, 5))
    github_button = tk.Button(help_frame, text="Github", command=lambda: webbrowser.open("https://github.com/TakiiiNotFound/ITR2ModManager"))
    github_button.pack(side="top", anchor="nw", padx=20, pady=5)
    
    discord_label = tk.Label(help_frame, text="Into The Radius Discord Server", fg="white", bg="#171717")
    discord_label.pack(side="top", anchor="nw", padx=20, pady=(20, 5))
    discord_button = tk.Button(help_frame, text="Join", command=help_logic.open_join)
    discord_button.pack(side="top", anchor="nw", padx=20, pady=5)
    
    support_label = tk.Label(help_frame, text="ITR2 Mod Manager support", fg="white", bg="#171717")
    support_label.pack(side="top", anchor="nw", padx=20, pady=(20, 5))
    support_button = tk.Button(help_frame, text="link", command=lambda: webbrowser.open("https://discord.com/channels/537645945006063636/1359296792889659493"))
    support_button.pack(side="top", anchor="nw", padx=20, pady=5)
    
    def on_tab_changed(event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Mods":
            expanded = get_expanded_paths(mods_tree)
            populate_mods_tree(mods_tree, expanded)
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    root.mainloop()

if __name__ == "__main__":
    start_ui()
