import os
import shutil
import config

# Global dictionary mapping Treeview item IDs to mod item structures.
mod_items = {}

def scan_folder(folder_path, parent=None):
    """
    Recursively scans a folder and returns a dictionary with:
      - name: the folder's basename
      - type: one of "mod", "fomod", "module", or "unknown"
      - path: the full folder path
      - children: a list of scanned subfolders (if any)
      - parent: the parent mod item (or None for top-level)
    
    Determination is based on the presence of files named "mod", "fomod", or "module".
    If none of these are found, the folder is marked as "unknown".
    """
    folder_name = os.path.basename(folder_path)
    mod_file = os.path.join(folder_path, "mod")
    fomod_file = os.path.join(folder_path, "fomod")
    module_file = os.path.join(folder_path, "module")
    
    item = {
        "name": folder_name,
        "path": folder_path,
        "children": [],
        "parent": parent
    }
    
    if os.path.exists(mod_file):
        item["type"] = "mod"
        return item
    elif os.path.exists(fomod_file):
        item["type"] = "fomod"
        for sub in os.listdir(folder_path):
            sub_path = os.path.join(folder_path, sub)
            if os.path.isdir(sub_path):
                if os.path.exists(os.path.join(sub_path, "module")):
                    child = {"name": sub, "type": "module", "path": sub_path, "children": [], "parent": item}
                    item["children"].append(child)
                else:
                    item["children"].append(scan_folder(sub_path, parent=item))
        return item
    elif os.path.exists(module_file):
        item["type"] = "module"
        return item
    else:
        item["type"] = "unknown"
        for sub in os.listdir(folder_path):
            sub_path = os.path.join(folder_path, sub)
            if os.path.isdir(sub_path):
                item["children"].append(scan_folder(sub_path, parent=item))
        return item

def get_mods_structure():
    """
    Scans the Mods directory (%itr2_path%/IntoTheRadius2/Content/Paks/Mods) and returns
    a list of mod structures.
    Recognized mods (types "mod", "fomod", or "module") are returned first; then unknowns.
    """
    mods = []
    unknowns = []
    cfg = config.load_config()
    itr2_path = cfg.get("itr2_path", "")
    if not itr2_path or not os.path.exists(itr2_path):
        return mods

    mods_dir = os.path.join(itr2_path, "IntoTheRadius2", "Content", "Paks", "Mods")
    if not os.path.exists(mods_dir):
        return mods

    for folder in os.listdir(mods_dir):
        folder_path = os.path.join(mods_dir, folder)
        if os.path.isdir(folder_path):
            item = scan_folder(folder_path, parent=None)
            if item["type"] == "unknown":
                unknowns.append(item)
            else:
                mods.append(item)
    mods.extend(unknowns)
    return mods

def insert_item(tree, parent, item, expanded_paths):
    """
    Recursively inserts an item into the Treeview.
    The main column displays "name (type)".
    The extra "is enable?" column displays "On" or "Off" for items that are not fomod or unknown.
    For fomod items, this column is left empty.
    The "Delete" column always displays "X".
    Unknown items get the "unknown" tag so they display in red.
    If the item's path is in expanded_paths, the item is expanded.
    Also saves the tree item id in mod_items.
    """
    off_file = os.path.join(item["path"], "off")
    if item["type"] == "fomod":
        state = ""
    elif item["type"] != "unknown":
        state = "Off" if os.path.exists(off_file) else "On"
    else:
        state = ""
    delete_text = "X"
    text = f"{item['name']} ({item['type']})"
    tags = ("unknown",) if item["type"] == "unknown" else ()
    item_id = tree.insert(parent, "end", text=text, values=(state, delete_text), tags=tags)
    item["tree_id"] = item_id
    mod_items[item_id] = item
    if item["path"] in expanded_paths:
        tree.item(item_id, open=True)
    for child in item.get("children", []):
        insert_item(tree, item_id, child, expanded_paths)

def populate_mods_tree(tree, expanded_paths=set()):
    """
    Clears the Treeview and populates it with the mods structure.
    expanded_paths is a set of folder paths that should be expanded.
    """
    global mod_items
    mod_items.clear()
    mods = get_mods_structure()
    for i in tree.get_children():
        tree.delete(i)
    for mod in mods:
        insert_item(tree, "", mod, expanded_paths)

def process_folder(folder, turning_off=True):
    """
    Recursively processes the folder:
      - When turning off, for each file with extension .pak, .ucas, or .utoc (if not already ending with .off),
        renames it by appending ".off". In every directory (current and subfolders), creates an "off" file.
      - When turning on, for each file ending with those extensions with ".off", renames it by removing ".off".
        Also, every "off" file found is removed.
    """
    target_exts = ['.pak', '.ucas', '.utoc']
    for root_dir, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root_dir, file)
            if turning_off:
                for ext in target_exts:
                    if file.lower().endswith(ext) and not file.lower().endswith(ext + ".off"):
                        new_name = file + ".off"
                        os.rename(full_path, os.path.join(root_dir, new_name))
                        break
            else:
                for ext in target_exts:
                    if file.lower().endswith(ext + ".off"):
                        new_name = file[:-4]
                        os.rename(full_path, os.path.join(root_dir, new_name))
                        break
        off_file_path = os.path.join(root_dir, "off")
        if turning_off:
            if not os.path.exists(off_file_path):
                try:
                    with open(off_file_path, "w") as f:
                        f.write("")
                except Exception:
                    pass
        else:
            if os.path.exists(off_file_path):
                try:
                    os.remove(off_file_path)
                except Exception:
                    pass

def toggle_mod_state(item):
    """
    Toggles the state of the mod item based on its folder:
      - If the folder is currently on (no "off" file in its main folder), turns it off by processing all files
        and creating an "off" file in every directory.
      - If the folder is off, turns it on by processing all files and removing all "off" files.
      Additionally, if a child (non-fomod) is toggled on while its parent's (fomod) off file exists,
      the parent's off file is removed (turning the parent on).
    
    Returns the new state ("On" or "Off").
    (Note: Toggling is disabled for fomod items.)
    """
    # If item is a fomod, do nothing.
    if item.get("type") == "fomod":
        return None
    folder = item.get("path")
    if not folder or not os.path.exists(folder):
        return None
    main_off_file = os.path.join(folder, "off")
    if item["type"] != "fomod" and item.get("parent") and item["parent"].get("type") == "fomod":
        parent = item["parent"]
        parent_off_file = os.path.join(parent["path"], "off")
        if os.path.exists(parent_off_file):
            process_folder(parent["path"], turning_off=False)
    if os.path.exists(main_off_file):
        process_folder(folder, turning_off=False)
        return "On"
    else:
        process_folder(folder, turning_off=True)
        return "Off"

def delete_mod(item):
    """
    Deletes the mod folder (recursively) for the given mod item.
    Returns True if deletion was successful.
    """
    folder = item.get("path")
    if folder and os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            return True
        except Exception:
            return False
    return False
