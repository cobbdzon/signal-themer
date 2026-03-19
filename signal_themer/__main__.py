import os
import platform
import shutil
import sys

import asarPy


# to make pyright shut up
def get_localappdata():
    localappdata_path = os.getenv("LOCALAPPDATA", "")
    if localappdata_path == "":
        return sys.exit("No LOCALAPPDATA environment variable found!")
    # return if it exists
    return localappdata_path


# main function that extracts the asar, calls other functions and packs it
def theme_injector():
    asar_file = get_asar_file_path()
    temp_path = get_temp_path()
    theme_file = get_selected_theme_file_path()

    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)

    # backup asar file
    if not os.path.isfile(asar_file + ".bak"):
        shutil.copy(asar_file, asar_file + ".bak")

    try:
        asarPy.extract_asar(asar_file, temp_path)
    except PermissionError:
        sys.exit("PermissionError: please use the command with sudo.")

    shutil.copy(theme_file, os.path.join(temp_path, "stylesheets", "theme.css"))
    import_theme(os.path.join(temp_path, "stylesheets", "manifest.css"))
    asarPy.pack_asar(temp_path, asar_file)

    shutil.rmtree(temp_path)


# returns path of signal-desktop
def get_asar_file_path():
    match platform.system():
        case "Linux" if os.path.isfile("/usr/lib/signal-desktop/resources/app.asar"):
            return "/usr/lib/signal-desktop/resources/app.asar"
        case "Linux" if os.path.isfile(
            "/var/lib/flatpak/app/org.signal.Signal/current/active/files/Signal/resources/app.asar"
        ):
            return "/var/lib/flatpak/app/org.signal.Signal/current/active/files/Signal/resources/app.asar"
        case "Windows":
            return os.path.join(
                get_localappdata(),
                r"Programs\signal-desktop\resources\app.asar",
            )
        case _:
            return sys.exit(
                "No asar file found, please report an issue in the github repo."
            )


# returns temp directory depending on os in order to temporily store extracted asar
def get_temp_path():
    current_os = platform.system()
    match current_os:
        case "Linux":
            return "/temp/signal-themer/"
        case "Windows":
            return os.path.join(get_localappdata(), r"temp\signal-themer")
        case _:
            return sys.exit(
                "No compatible temp folder found for your operating system: "
                + current_os
            )


# add @import css in front of a file
def import_theme(file_path):
    with open(file_path, "r+") as f:
        if f.readline().split(" ", 1)[0] != "@import":
            f.seek(0)
        data = f.read()
        f.seek(0)
        f.truncate()
        f.write("@import 'theme.css';\n" + data)


# reads user argument to read theme path
def get_selected_theme_file_path():
    if len(sys.argv) != 2:
        sys.exit("Wrong number of argument, try `signal-themer <path-to-theme.css>`")
    elif not os.path.isfile(sys.argv[1]):
        sys.exit("The theme you entered doesn't exist! Try again.")
    elif not sys.argv[1].endswith(".css"):
        sys.exit("The theme must be a css file.")
    return sys.argv[1]


if __file__ == "__main__":
    theme_injector()
