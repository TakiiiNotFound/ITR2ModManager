import os
import webbrowser
import customtkinter as ctk
from PIL import Image
import settings  # Import the settings module
from mods import ModsTreeView  # For the "Mods" sub-tab

# Force dark mode and set the default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mod Manager")
        self.geometry("960x720")
        self.resizable(False, False)
        
        # Set window icon from %APPDATA%\ITR2ModManager\Media\icon.ico
        icon_path = os.path.join(os.getenv("APPDATA"), "ITR2ModManager", "Media", "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Header with banner image
        self.header_frame = ctk.CTkFrame(self, height=55, fg_color="#1a1a1a")
        self.header_frame.pack(side="top", fill="x")

        banner_path = os.path.join(os.getenv("APPDATA"), "ITR2ModManager", "Media", "banner.png")
        try:
            banner_img = Image.open(banner_path)
            # Increase width by 8%: size (216, 55)
            self.banner_image = ctk.CTkImage(banner_img, size=(216, 55))
            self.banner_label = ctk.CTkLabel(self.header_frame, image=self.banner_image, text="")
            self.banner_label.pack(side="left", padx=10, pady=5)
        except Exception as e:
            print(f"Error loading banner image from {banner_path}: {e}")

        # Main area splits into navigation (left) and content (right)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Navigation background: 10% darker than "#2b2b2b"
        nav_bg = "#272727"

        self.navigation_frame = ctk.CTkFrame(self.main_frame, width=200, fg_color=nav_bg)
        self.navigation_frame.pack(side="left", fill="y")

        self.nav_tabs_frame = ctk.CTkFrame(self.navigation_frame, fg_color=nav_bg)
        self.nav_tabs_frame.pack(side="top", fill="both", expand=True)

        self.nav_bottom_frame = ctk.CTkFrame(self.navigation_frame, fg_color=nav_bg)
        self.nav_bottom_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=0)

        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Create main tabs for "Mods", "Install", "Settings", "Help"
        self.tabs = {}
        for tab in ["Mods", "Install", "Settings", "Help"]:
            btn = ctk.CTkButton(self.nav_tabs_frame, text=tab, command=lambda t=tab: self.show_tab(t))
            btn.pack(pady=10, padx=20, fill="x")
            self.tabs[tab] = ctk.CTkFrame(self.content_frame)

        # Populate tabs.
        self.populate_mods_tab()
        self.populate_install_tab()
        self.populate_help_tab()
        self.populate_settings_tab()

        # Additional bottom navigation buttons.
        self.launch_itr2_button = ctk.CTkButton(self.nav_bottom_frame, text="Launch ITR2", command=self.launch_itr2)
        self.launch_itr2_button.pack(pady=(4,2), padx=20, fill="x")
        self.more_mods_button = ctk.CTkButton(self.nav_bottom_frame, text="More Mods", command=self.more_mods)
        self.more_mods_button.pack(pady=(2,4), padx=20, fill="x")
        self.tool_label = ctk.CTkLabel(self.nav_bottom_frame, text="Tool by TakiiiNotFound", font=("Arial", 10), text_color="gray")
        self.tool_label.pack(pady=(2, 4))

        # Show default main tab ("Mods")
        self.show_tab("Mods")
 
    def show_tab(self, tab_name: str):
        for frame in self.tabs.values():
            frame.pack_forget()
        self.tabs[tab_name].pack(fill="both", expand=True)
        if tab_name == "Mods":
            self.show_mods_subtab("Mods")
 
    def populate_mods_tab(self):
        mods_tab = self.tabs["Mods"]
 
        # Container for nested sub-tab navigation in "Mods" tab.
        self.mods_subnav = ctk.CTkFrame(mods_tab, fg_color="#2b2b2b")
        self.mods_subnav.pack(side="top", fill="x")
 
        # Container for nested sub-tab content.
        self.mods_subcontent = ctk.CTkFrame(mods_tab)
        self.mods_subcontent.pack(side="top", fill="both", expand=True)
 
        self.mods_subtabs = {}
        sub_tab_names = ["Mods", "LogicMods", "LuaMods"]
 
        for name in sub_tab_names:
            btn = ctk.CTkButton(self.mods_subnav, text=name, command=lambda n=name: self.show_mods_subtab(n))
            btn.pack(side="left", padx=5, pady=5)
            if name == "LuaMods":
                self.lua_mods_btn = btn  # Reference for advanced mode enabling/disabling.
            frame = ctk.CTkFrame(self.mods_subcontent)
            self.mods_subtabs[name] = frame
 
        self.show_mods_subtab("Mods")
 
    def show_mods_subtab(self, name):
        for frame in self.mods_subtabs.values():
            frame.pack_forget()
        if name == "Mods":
            for widget in self.mods_subtabs[name].winfo_children():
                widget.destroy()
            scroll_frame = ctk.CTkScrollableFrame(self.mods_subtabs[name])
            scroll_frame.pack(fill="both", expand=True)
            from mods import ModsTreeView
            tree = ModsTreeView(scroll_frame)
            tree.pack(fill="both", expand=True)
        elif name == "LogicMods":
            for widget in self.mods_subtabs[name].winfo_children():
                widget.destroy()
            scroll_frame = ctk.CTkScrollableFrame(self.mods_subtabs[name])
            scroll_frame.pack(fill="both", expand=True)
            from logicmods import LogicModsTreeView
            tree = LogicModsTreeView(scroll_frame)
            tree.pack(fill="both", expand=True)
        elif name == "LuaMods":
            for widget in self.mods_subtabs[name].winfo_children():
                widget.destroy()
            scroll_frame = ctk.CTkScrollableFrame(self.mods_subtabs[name])
            scroll_frame.pack(fill="both", expand=True)
            from luamods import LuaModsListView
            list_view = LuaModsListView(scroll_frame)
            list_view.pack(fill="both", expand=True)
            warning_label = ctk.CTkLabel(scroll_frame, 
                text="Deleting some Lua mods can break others; be sure to know what you are doing",
                font=("Arial", 10), text_color="red")
            warning_label.pack(pady=(5, 10))
        self.mods_subtabs[name].pack(fill="both", expand=True)
 
    def populate_install_tab(self):
        install_tab = self.tabs["Install"]
        # For Basic Mod Install.
        basic_frame = ctk.CTkFrame(install_tab)
        basic_frame.pack(pady=10, padx=20, fill="x")
        basic_label = ctk.CTkLabel(basic_frame, text="Basic Mod Install", font=("Arial", 14))
        basic_label.pack(pady=(5,5))
        basic_button = ctk.CTkButton(basic_frame, text="Install", command=self.install_basic_mod)
        basic_button.pack(pady=(5,10))
 
        # For Fomod Mod Install.
        fomod_frame = ctk.CTkFrame(install_tab)
        fomod_frame.pack(pady=10, padx=20, fill="x")
        fomod_label = ctk.CTkLabel(fomod_frame, text="Fomod Mod Install", font=("Arial", 14))
        fomod_label.pack(pady=(5,5))
        fomod_button = ctk.CTkButton(fomod_frame, text="Install", command=self.install_fomod_mod)
        fomod_button.pack(pady=(5,10))
 
    def populate_help_tab(self):
        help_tab = self.tabs["Help"]
        help_items = [
            {"text": "ITR2 Mod Manager Github Page", "button": "Github", "link": "https://github.com/TakiiiNotFound/ITR2ModManager"},
            {"text": "Into The Radius Discord Server", "button": "Join", "link": "https://discord.com/invite/itr"},
            {"text": "Into The Radius Modding Community Server", "button": "Join", "link": "https://discord.gg/ZPxkqVXPWM"},
            {"text": "ITR2 Mod Manager Support", "button": "See channel", "link": "https://discord.com/channels/537645945006063636/1021537057845301298/threads/1359296792889659493"}
        ]
 
        for item in help_items:
            container = ctk.CTkFrame(help_tab)
            container.pack(pady=10, padx=20, fill="x")
            label = ctk.CTkLabel(container, text=item["text"], font=("Arial", 14))
            label.pack(pady=(10,5))
            button = ctk.CTkButton(container, text=item["button"],
                                   command=lambda link=item["link"]: webbrowser.open(link))
            button.pack(pady=(5,10))
 
    def populate_settings_tab(self):
        settings_tab = self.tabs["Settings"]
 
        settings_container = ctk.CTkFrame(settings_tab, fg_color="#2b2b2b", border_width=1, border_color="#5e5e5e")
        settings_container.pack(pady=20, padx=20, fill="x")
 
        folder_label = ctk.CTkLabel(settings_container, text="ITR2 Game Folder", font=("Arial", 14), anchor="w")
        folder_label.pack(pady=(10,5), padx=10, fill="x")
 
        row_container = ctk.CTkFrame(settings_container, fg_color="#2b2b2b")
        row_container.pack(pady=(0,10), padx=10, fill="x")
 
        self.game_folder_entry = ctk.CTkEntry(row_container, placeholder_text="Select game folder path")
        self.game_folder_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        current_path = settings.get_ITR2_Path()
        if current_path:
            self.game_folder_entry.insert(0, current_path)
 
        buttons_frame = ctk.CTkFrame(row_container, fg_color="#2b2b2b")
        buttons_frame.pack(side="right")
 
        select_button = ctk.CTkButton(buttons_frame, text="Select", command=self.select_game_folder)
        select_button.pack(pady=(0,5), fill="x")
        check_button = ctk.CTkButton(buttons_frame, text="Check Game Path", command=lambda: settings.check_game_path(self))
        check_button.pack(fill="x")
 
        change_load_order_button = ctk.CTkButton(settings_tab, text="Change Load Order", command=self.change_load_order)
        change_load_order_button.pack(pady=(0,20), padx=20, fill="x")
 
        # Advanced mode checkbox, default state based on config.
        self.advanced_mode_var = ctk.BooleanVar(value=settings.get_AdvancedMode())
        self.advanced_mode_checkbox = ctk.CTkCheckBox(settings_tab, text="Advanced mode", variable=self.advanced_mode_var, command=self.toggle_advanced_mode)
        self.advanced_mode_checkbox.pack(pady=(0,20), padx=20, fill="x")
        self.toggle_advanced_mode()
 
    def toggle_advanced_mode(self):
        settings.set_AdvancedMode(self.advanced_mode_var.get())
        if self.advanced_mode_var.get():
            self.lua_mods_btn.configure(state="normal")
        else:
            self.lua_mods_btn.configure(state="disabled")
            self.show_mods_subtab("Mods")
 
    def install_basic_mod(self):
        from basic_install import open_basic_install_window
        open_basic_install_window(self)
 
    def install_fomod_mod(self):
        from fomod_install import open_fomod_install_window
        open_fomod_install_window(self)
 
    def launch_itr2(self):
        webbrowser.open("steam://rungameid/2307350")
 
    def more_mods(self):
        webbrowser.open("https://www.nexusmods.com/games/intotheradius2/mods")
 
    def select_game_folder(self):
        folder = settings.select_ITR2_folder()
        if folder:
            self.game_folder_entry.delete(0, ctk.END)
            self.game_folder_entry.insert(0, folder)
 
    def check_game_path(self):
        settings.check_game_path(self)
 
    def change_load_order(self):
        from load_order import open_load_order_window
        open_load_order_window(self)
 
if __name__ == "__main__":
    app = ModManagerApp()
    app.mainloop()
