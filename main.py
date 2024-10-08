import glob
import os
import shutil
import sys
import tkinter as tk
import xml.etree.ElementTree as ET
import zipfile
from tkinter import filedialog, messagebox


def find_files(folder):
    return glob.glob(os.path.join(folder, '**', '*.*'), recursive=True)


def there_are_scripts(folder):
    return len(glob.glob(os.path.join(folder, '**', '*.sxp'), recursive=True)) > 0


def is_valid_sqx_folder(folder):
    sqx_sub_files = (
        os.path.join(folder, "StrategyQuantX.exe"),
        os.path.join(folder, "sqcli.exe"),
        os.path.join(folder, "CodeEditor.exe"),
    )

    return all(os.path.exists(file) for file in sqx_sub_files)


def is_valid_mt5_folder(mt5_folder):
    mt5_sub_folders = (
        os.path.join(mt5_folder, "MQL5"),
        os.path.join(mt5_folder, "bases"),
        os.path.join(mt5_folder, "config"),
    )
    return all(os.path.exists(folder) for folder in mt5_sub_folders)


def there_are_internal_script(zip_files, sqx_folder):
    internal_sqx_folder = os.path.join(sqx_folder, 'internal')

    for file in zip_files:
        internal_file = os.path.join(internal_sqx_folder, file)

        if os.path.exists(internal_file):
            return True

    return False


def install_sxp_file(file, sqx_folder, destination):
    uninstalled_file = None
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_files = zip_ref.namelist()
            if not there_are_internal_script(zip_files, sqx_folder):
                zip_ref.extractall(destination)
            else:
                uninstalled_file = file
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "Invalid .sxp file format.")
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Unknown error {e}.")

    return uninstalled_file


def install_mql5_file(file, destination):
    indicators_folder = os.path.join(destination, 'Metatrader5', 'Indicators')
    if not os.path.exists(indicators_folder):
        os.mkdir(indicators_folder)
    shutil.copy(file, indicators_folder)


def install_mqh_file(file, destination):
    include_folder = os.path.join(destination, 'Metatrader5', 'Include')
    if not os.path.exists(include_folder):
        os.mkdir(include_folder)
    shutil.copy(file, include_folder)


def install_mql4_file(file, destination):
    indicators_folder = os.path.join(destination, 'Metatrader4', 'Indicators')
    if not os.path.exists(indicators_folder):
        os.mkdir(indicators_folder)
    shutil.copy(file, indicators_folder)


def install_tradestation_file(file, destination):
    tradestation_folder = os.path.join(destination, 'Tradestation')
    if not os.path.exists(tradestation_folder):
        os.mkdir(tradestation_folder)
    shutil.copy(file, tradestation_folder)


def install_custom_blocks_files(file, destination):
    custom_blocks_file = os.path.join(destination, 'settings', 'customBlocks.xml')

    try:
        element_tree = ET.parse(custom_blocks_file)
        root_element = element_tree.getroot()
    except FileNotFoundError:
        root_element = ET.Element('CustomBlocks')
        element_tree = ET.ElementTree(root_element)

    items = root_element.findall("Item")

    try:
        file_element = ET.parse(file).getroot()
    except Exception as e:
        messagebox.showerror("Error", f"Unknown error {e}.")
        return

    file_items = file_element.findall("Item")
    for file_item in file_items:
        if len(items) == 0:
            root_element.append(file_item)
        else:
            root_item_key_values = list()
            for item in items:
                root_item_key_values.append(item.attrib.get("key"))

            if file_item.attrib.get("key") not in root_item_key_values:
                root_element.append(file_item)

    element_tree.write(custom_blocks_file, encoding='utf-8', xml_declaration=True)


def install_into_mt5(sqx_folder, mt5_folder):
    custom_indicator_folder = os.path.join(sqx_folder, "custom_indicators", "MetaTrader5")
    mql5_folder = os.path.join(mt5_folder, "MQL5")

    shutil.copytree(custom_indicator_folder, mql5_folder, dirs_exist_ok=True)


def install_custom_indicators():
    scripts_folder = entry_scripts_folder.get()
    sqx_folder = entry_sqx_folder.get()
    mt5_folder = entry_mt5_folder.get()
    user_sqx_folder = os.path.join(sqx_folder, 'user')
    custom_indicators_folder = os.path.join(sqx_folder, 'custom_indicators')
    files = find_files(scripts_folder)

    if not there_are_scripts(scripts_folder):
        messagebox.showinfo("Empty scripts",
                            "You are selecting an empty scripts folder, please select the correct one.")
        return

    if not is_valid_sqx_folder(sqx_folder):
        messagebox.showerror("Invalid SQX folder",
                             "You are selecting an invalid SQX folder, please select the correct one.")
        return

    if mt5_folder != "" and not is_valid_mt5_folder(mt5_folder):
        messagebox.showerror("Invalid MT5 folder",
                             "You are selecting an invalid MT5 folder, please select the correct one.")
        return

    uninstalled_files = []
    for file in files:
        _, file_extension = os.path.splitext(file)
        file_extension = file_extension.lower()
        if file_extension == ".sxp":
            uninstalled_file = install_sxp_file(file, sqx_folder, user_sqx_folder)
            if uninstalled_file is not None:
                uninstalled_files.append(uninstalled_file)
        elif file_extension == ".mq5":
            install_mql5_file(file, custom_indicators_folder)
        elif file_extension == ".mqh":
            install_mqh_file(file, custom_indicators_folder)
        elif file_extension == ".mq4":
            install_mql4_file(file, custom_indicators_folder)
        elif file_extension == ".eld":
            install_tradestation_file(file, custom_indicators_folder)
        elif file_extension == ".xml":
            install_custom_blocks_files(file, user_sqx_folder)

    if mt5_folder != "":
        install_into_mt5(sqx_folder, mt5_folder)

    if len(uninstalled_files) == 0:
        messagebox.showinfo("Installation success", "The installation is finished!.")
    else:
        uninstalled_files_str = ""
        for file in uninstalled_files:
            uninstalled_files_str += f"{file}\n"

        messagebox.showinfo("Installation finished",
                            f"The installation is finished!.\nThere are some files that couldn't be installed because "
                            f"already exist in SQX: \n\n {uninstalled_files}")


def select_folder(entry):
    folder = filedialog.askdirectory()
    if folder:
        entry.delete(0, tk.END)
        entry.insert(0, folder)


def show_explanation():
    msg = (
        "To install the scripts:\n"
        "0. Close StrategyQuant X\n"
        "1. Select the folder with the downloaded scripts.\n"
        "2. Select the folder where your SQX is installed.\n"
        "3. Select the folder where your MT5 Terminal is installed. (To get this, go to Metatrades 5 > File > Open Data Folder and copy the path)\n"
        "4. Press Install button.\n"
        "5. Restart StrategyQuant X.\n"
    )
    messagebox.showinfo("Install info", msg)


def show_about_me():
    msg = (
        "SQXIndicatorInstaller v0.3\n\n"
        "Author: Javier Luque\n"
        "GitHub: https://github.com/javils\n"
    )
    messagebox.showinfo("About me", msg)


def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


root = tk.Tk()
root.title("SQX Custom Indicators Installer")
root.resizable(False, False)
width = 500
height = 200
x = (root.winfo_screenwidth() - width) // 2
y = (root.winfo_screenheight() - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)

help_menu.add_command(label="Install info", command=show_explanation)
help_menu.add_command(label="About me", command=show_about_me)

label_scripts_folder = tk.Label(root, text="Folder with scripts:")
label_scripts_folder.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

entry_scripts_folder = tk.Entry(root, width=50)
entry_scripts_folder.grid(row=0, column=1, padx=10, pady=10)

button_scripts_folder_selector = tk.Button(root, text="...", command=lambda: select_folder(entry_scripts_folder))
button_scripts_folder_selector.grid(row=0, column=2, padx=10, pady=10)

label_sqx_folder = tk.Label(root, text="SQX Folder:")
label_sqx_folder.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

entry_sqx_folder = tk.Entry(root, width=50)
entry_sqx_folder.grid(row=1, column=1, padx=10, pady=10)

button_scripts_sqx_folder_selector = tk.Button(root, text="...", command=lambda: select_folder(entry_sqx_folder))
button_scripts_sqx_folder_selector.grid(row=1, column=2, padx=10, pady=10)

label_mt5_folder = tk.Label(root, text="MT5 Terminal Folder:")
label_mt5_folder.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

entry_mt5_folder = tk.Entry(root, width=50)
entry_mt5_folder.grid(row=2, column=1, padx=10, pady=10)

button_scripts_mt5_folder_selector = tk.Button(root, text="...", command=lambda: select_folder(entry_mt5_folder))
button_scripts_mt5_folder_selector.grid(row=2, column=2, padx=10, pady=10)

button_install = tk.Button(root, text="Install", command=install_custom_indicators)
button_install.grid(row=3, column=0, columnspan=3, pady=20)

# This is here because a bug, if I put the icon in the top of the program, then the sizes of the windows changes.
root.iconbitmap(get_resource_path("./icon/icon.ico"))
root.mainloop()
