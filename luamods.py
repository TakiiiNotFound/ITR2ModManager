import os
import shutil
import customtkinter as ctk
import settings  # To obtain ITR2_Path from config

class LuaModsFolderItem(ctk.CTkFrame):
    def __init__(self, parent, folder_name, folder_path, refresh_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.folder_name = folder_name
        self.folder_path = folder_path
        self.refresh_callback = refresh_callback
        
        # Create header frame for each LuaMods folder item.
        header = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        header.pack(fill="x", padx=10, pady=2)
        
        self.label = ctk.CTkLabel(header, text=self.folder_name, anchor="w")
        self.label.pack(side="left", fill="x", expand=True)
        
        # X delete button.
        self.delete_button = ctk.CTkButton(header, text="X", width=20, fg_color="#ff5555",
                                           hover_color="#ff0000", command=self.confirm_delete, corner_radius=5)
        self.delete_button.pack(side="right", padx=5)
        
    def confirm_delete(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Delete Folder")
        width, height = 300, 120
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.transient(self)
        popup.grab_set()
        
        msg = f"Are you sure to delete '{self.folder_name}'?"
        label = ctk.CTkLabel(popup, text=msg)
        label.pack(pady=10, padx=10)
        
        btn_frame = ctk.CTkFrame(popup)
        btn_frame.pack(pady=10)
        yes_btn = ctk.CTkButton(btn_frame, text="Yes", width=60, command=lambda: self._delete_folder(popup))
        yes_btn.pack(side="left", padx=5)
        no_btn = ctk.CTkButton(btn_frame, text="No", width=60, command=popup.destroy)
        no_btn.pack(side="left", padx=5)
        popup.wait_window(popup)
        
    def _delete_folder(self, popup):
        try:
            shutil.rmtree(self.folder_path)
            popup.destroy()
            self.refresh_callback()
        except Exception as e:
            print(f"Error deleting folder {self.folder_path}: {e}")
            popup.destroy()

class LuaModsListView(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.build_list()

    def _get_luamods_path(self):
        itr2_path = settings.get_ITR2_Path()
        if not itr2_path:
            return None
        return os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "LuaMods")

    def build_list(self):
        for child in self.winfo_children():
            child.destroy()
        path = self._get_luamods_path()
        if not path or not os.path.isdir(path):
            ctk.CTkLabel(self, text="LuaMods folder not found or not set").pack(pady=20)
            return
        try:
            items = os.listdir(path)
        except Exception:
            items = []
        folders = sorted([d for d in items if os.path.isdir(os.path.join(path, d))], key=str.lower)
        if not folders:
            ctk.CTkLabel(self, text="No LuaMods found").pack(pady=20)
            return
        for folder in folders:
            folder_path = os.path.join(path, folder)
            item = LuaModsFolderItem(self, folder, folder_path, refresh_callback=self.build_list)
            item.pack(fill="x", pady=2)
