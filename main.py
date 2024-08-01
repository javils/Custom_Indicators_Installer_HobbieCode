import tkinter as tk
import zipfile
import os
import glob
import shutil
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET


def find_files(folder):
    return glob.glob(os.path.join(folder, '**', '*.*'), recursive=True)


def there_are_scripts(folder):
    return len(glob.glob(os.path.join(folder, '**', '*.sxp'), recursive=True)) > 0


def is_valid_sqx_folder(folder):
    files = glob.glob(os.path.join(folder, '**', '*.exe'), recursive=True)
    check_files = ["StrategyQuantX.exe", "sqcli.exe", "CodeEditor.exe"]

    file_names = [os.path.basename(file) for file in files]

    return all(check_file in file_names for check_file in check_files)


def install_sxp_file(file, destination):
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(destination)
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "Invalid .sxp file format.")
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Unknown error {e}.")


def install_mql5_file(file, destination):
    mt5_file = os.path.join(destination, 'Metatrader5', 'Indicators')
    shutil.copy(file, mt5_file)


def install_mqh_file(file, destination):
    mt5_file = os.path.join(destination, 'Metatrader5', 'Include')
    shutil.copy(file, mt5_file)


def install_mql4_file(file, destination):
    mt4_file = os.path.join(destination, 'Metatrader4', 'Indicators')
    shutil.copy(file, mt4_file)


def install_tradestation_file(file, destination):
    tradestation_file = os.path.join(destination, 'Tradestation')
    shutil.copy(file, tradestation_file)


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


def install_custom_indicators():
    scripts_folder = entry_scripts_folder.get()
    sqx_folder = entry_sqx_folder.get()
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

    for file in files:
        _, file_extension = os.path.splitext(file)
        file_extension = file_extension.lower()
        if file_extension == ".sxp":
            install_sxp_file(file, user_sqx_folder)
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

    messagebox.showinfo("Installation success",
                         "The installation is finished!.")


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
        "3. Press Install button.\n"
        "4. Restart StrategyQuant X.\n"
    )
    messagebox.showinfo("Install info", msg)


def show_about_me():
    msg = (
        "SQXIndicatorInstaller v0.1\n\n"
        "Author: Javier Luque\n"
        "GitHub: https://github.com/javils\n"
    )
    messagebox.showinfo("About me", msg)


root = tk.Tk()
root.title("SQX Custom Indicators Installer")
root.resizable(False, False)
width = 500
height = 150
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

button_install = tk.Button(root, text="Install", command=install_custom_indicators)
button_install.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
