import webbrowser

def open_tutorial():
    """Opens the Fomod setup tutorial URL."""
    webbrowser.open("https://youtu.be/dQw4w9WgXcQ")

def open_github():
    """Opens the ITR2 Mod Manager Github page."""
    webbrowser.open("https://github.com/TakiiiNotFound/ITR2ModManager")

def open_join():
    """Opens the Into The Radius Discord Server URL."""
    webbrowser.open("https://discord.gg/itr")

if __name__ == "__main__":
    # Test the functions if running this module directly
    open_tutorial()
    open_github()
    open_join()
