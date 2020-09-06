from formatter_functions import *
from zipfile import ZipFile
# from glob import glob
import tkinter as tk
from tkinter import filedialog
import os

cwd = os.getcwd()
input_zip = outputDir = recipName = ""

# ===== Functions used on tk buttons


def select_zip():
    global input_zip
    input_zip = filedialog.askopenfilename(initialdir=cwd, title="Select an exported chat",
                                           filetypes=[("Zip files", "*.zip")])


def select_output_dir():
    global outputDir
    outputDir = filedialog.askdirectory(initialdir="/", title="Select an output directory")


# ===== Tkinter stuff

root = tk.Tk()
root.title("WhatsApp Formatter")
root.geometry("500x300")

introMessage = tk.Label(root, text="Welcome to the WhatsApp Formatter!", anchor="n")
introMessage.pack()

select_zip_button = tk.Button(root, text="Select an exported chat", command=select_zip)
select_zip_button.pack()

select_output_button = tk.Button(root, text="Select an output directory", command=select_output_dir)
select_output_button.pack()

name_box_label = tk.Label(root, text="Enter the name of the recipient:")
name_box_label.pack()

enter_name_box = tk.Entry(root, textvariable=recipName)
enter_name_box.pack()

root.mainloop()
