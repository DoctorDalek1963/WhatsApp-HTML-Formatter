from formatter_functions import *
from zipfile import ZipFile
from glob import glob
import tkinter as tk
from tkinter import filedialog
import os

cwd = os.getcwd()
zip_file = ""


def select_zip():
    global zip_file
    zip_file = filedialog.askopenfilename(
        initialdir=cwd, title="Select an exported chat", filetypes=[("Zip files", "*.zip")])


root = tk.Tk()
root.title("WhatsApp Formatter")
root.geometry("500x300")

introMessage = tk.Label(root, text="Welcome to the WhatsApp Formatter!", anchor="n")
introMessage.pack()

zip_select_button = tk.Button(root, text="Select an exported chat", command=select_zip)
zip_select_button.pack()

root.mainloop()
