import os
import shutil
import customtkinter as ctk
import settings  # to get the ITR2_Path from config

FILE_EXTS = [".pak", ".ucas", ".utoc"]

class FolderTreeItem(ctk.CTkFrame):
    def __init__(self, parent, path, indent=0, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.path = path
        self.indent = indent
        self.expanded = False

        folder_name = os.path.basename(path)
        self.has_children = self._check_has_children()

        header_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
        header_frame.pack(fill="x")

        left_pad = self.indent if self.indent else 0

        if self.has_children:
            self.toggle_button = ctk.CTkButton(header_frame, text="+", width=20, command=self.toggle, corner_radius=5)
            self.toggle_button.pack(side="left", padx=(left_pad, 5))
        else:
            ctk.CTkLabel(header_frame, text=" ", width=20).pack(side="left", padx=(left_pad, 5))
        
        self.label = ctk.CTkLabel(header_frame, text=folder_name, anchor="w")
        self.label.pack(side="left", fill="x", expand=True)

        self.delete_button = ctk.CTkButton(header_frame, text="X", width=20, fg_color="#ff5555",
                                           hover_color="#ff0000", command=self.confirm_delete, corner_radius=5)
        self.delete_button.pack(side="right", padx=5)

        if not self.has_children:
            off_file = os.path.join(self.path, "off")
            default_state = False if os.path.exists(off_file) else True
            self.check_mod_var = ctk.BooleanVar(value=default_state)
            self.check_mod = ctk.CTkCheckBox(header_frame, text="", variable=self.check_mod_var, command=self.toggle_mod)
            self.check_mod.pack(side="right", padx=5)

        self.children_frame = None

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
        if not self.children_frame:
            self.children_frame = ctk.CTkFrame(self, fg_color=self.cget("fg_color"))
            self.children_frame.pack(fill="x", padx=10)
            self._populate_children()
        else:
            self.children_frame.pack(fill="x", padx=10)

    def collapse(self):
        self.expanded = False
        if hasattr(self, "toggle_button"):
            self.toggle_button.configure(text="+")
        if self.children_frame:
            self.children_frame.forget()

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
            child = FolderTreeItem(self.children_frame, sub, indent=self.indent + 10)
            child.pack(fill="x", pady=2)

    def toggle_mod(self):
        off_file = os.path.join(self.path, "off")
        is_enabled = self.check_mod_var.get()
        if is_enabled:
            if os.path.exists(off_file):
                os.remove(off_file)
            self._rename_files(add_off=False)
        else:
            try:
                with open(off_file, "w") as f:
                    f.write("")
            except Exception as e:
                print(f"Error creating off file in {self.path}: {e}")
            self._rename_files(add_off=True)

    def _rename_files(self, add_off=True):
        try:
            for item in os.listdir(self.path):
                full_item = os.path.join(self.path, item)
                if os.path.isfile(full_item):
                    for ext in FILE_EXTS:
                        if add_off:
                            if item.endswith(ext) and not item.endswith(ext + ".off"):
                                new_name = item + ".off"
                                os.rename(full_item, os.path.join(self.path, new_name))
                        else:
                            if item.endswith(ext + ".off"):
                                new_name = item[:-4]
                                os.rename(full_item, os.path.join(self.path, new_name))
        except Exception as e:
            print(f"Error renaming files in {self.path}: {e}")

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
        msg = f"Are you sure to delete {os.path.basename(self.path)}?"
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
            shutil.rmtree(self.path)
            popup.destroy()
            self.destroy()
        except Exception as e:
            print(f"Error deleting folder {self.path}: {e}")
            popup.destroy()

class LogicModsTreeView(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.mods_path = self._get_mods_path()
        self.build_tree()

    def _get_mods_path(self):
        itr2_path = settings.get_ITR2_Path()
        if not itr2_path:
            return None
        # Use LogicMods folder instead of Mods.
        return os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "LogicMods")

    def build_tree(self):
        for child in self.winfo_children():
            child.destroy()
        if not self.mods_path or not os.path.isdir(self.mods_path):
            ctk.CTkLabel(self, text="LogicMods folder not found or not set").pack(pady=20)
            return
        try:
            items = os.listdir(self.mods_path)
        except Exception:
            items = []
        folders = sorted(
            [os.path.join(self.mods_path, d) for d in items if os.path.isdir(os.path.join(self.mods_path, d))],
            key=lambda x: os.path.basename(x).lower()
        )
        if not folders:
            ctk.CTkLabel(self, text="No LogicMods found").pack(pady=20)
        for folder in folders:
            item = FolderTreeItem(self, folder, indent=10)
            item.pack(fill="x", pady=2)
