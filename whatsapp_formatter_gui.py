# WhatsApp-Formatter is a program that takes exported WhatsApp chats and
# formats them into more readable HTML files, with embedded attachments.
#
# Copyright (C) 2020 Doctor Dalek <https://github.com/DoctorDalek1963>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from tkinter import filedialog, StringVar
from formatter_functions import *
from time import sleep
import tkinter as tk
import threading
import os

cwd = os.getcwd()
inputZip = outputDir = recipName = ""
finishExportFlag = startExportFlag = False

descriptionText = """Steps:\n
1. Select an exported chat\n
2. Select an export directory\n
3. Enter the name of the recipient (case sensitive)\n
4. Click the format button\n
5. The format button will be greyed out\n
6. Wait until it's active again\n
7. Choose a new zip to format or exit the program"""

default_x_padding = 10
default_y_padding = 5
dedicated_padding_y = 15

# ===== Functions used on tk buttons


def select_zip():
    global inputZip
    inputZip = filedialog.askopenfilename(initialdir=cwd, title="Select an exported chat",
                                          filetypes=[("Zip files", "*.zip")])


def select_output_dir():
    global outputDir
    outputDir = filedialog.askdirectory(initialdir="/", title="Select an output directory")


def begin_export():
    global startExportFlag, finishExportFlag
    startExportFlag = True
    sleep(0.1)  # Wait and let Format button update

    extract_thread = threading.Thread(extract_zip(inputZip))
    file_write_thread = threading.Thread(write_to_file(recipName, outputDir))
    extract_thread.start()
    file_write_thread.start()
    sleep(1)
    extract_thread.join()
    file_write_thread.join()

    # # TODO: Use new 'threading' module to wait until thread is finished
    # t = threading.Thread(target=update_loop)
    # t.start()
    # t.join()

    finishExportFlag = True


begin_export_thread = threading.Thread(begin_export())


def begin_export_thread_func():
    begin_export_thread.start()


# ===== Tkinter initialisation

# Initialisation of window
root = tk.Tk()
root.title("WhatsApp Formatter")
root.resizable(False, False)

selected_zip_var = StringVar()
selected_output_var = StringVar()


# ===== Create widgets

# Create padding widgets
middle_column_padding = tk.LabelFrame(root)
row_padding_1 = tk.LabelFrame(root)
row_padding_2 = tk.LabelFrame(root)
row_padding_3 = tk.LabelFrame(root)
row_padding_4 = tk.LabelFrame(root)

# Create input widgets
select_zip_button = tk.Button(root, text="Select an exported chat", command=select_zip, bd=3)
selected_zip_label = tk.Label(root, textvariable=selected_zip_var)

select_output_button = tk.Button(root, text="Select an output directory", command=select_output_dir, bd=3)
selected_output_label = tk.Label(root, textvariable=selected_output_var)

name_box_label = tk.Label(root, text="Enter the name of the recipient:")
enter_name_box = tk.Entry(root)

# Instructions for use
description_label = tk.Label(root, text=descriptionText)

# Create special button widgets
format_button = tk.Button(root, text="Format", command=begin_export_thread_func, state="disabled", bd=3)
exit_button = tk.Button(root, text="Exit", command=root.destroy, bd=3)


# ===== Place widgets

# Spacing between instructions & inputs
middle_column_padding.grid(row=1, rowspan=9, column=1, padx=20)

row_padding_1.grid(row=4, column=2, pady=dedicated_padding_y)

# Select zip and display name
select_zip_button.grid(row=2, column=2, padx=default_x_padding, pady=default_y_padding)
selected_zip_label.grid(row=3, column=2, padx=default_x_padding, pady=default_y_padding)

row_padding_2.grid(row=4, column=2, pady=dedicated_padding_y)

# Select output directory and display it
select_output_button.grid(row=5, column=2, padx=default_x_padding, pady=default_y_padding)
selected_output_label.grid(row=6, column=2, padx=default_x_padding, pady=default_y_padding)

row_padding_3.grid(row=7, column=2, pady=dedicated_padding_y)

# Enter recipient name
name_box_label.grid(row=8, column=2, padx=default_x_padding, pady=default_y_padding)
enter_name_box.grid(row=9, column=2, padx=default_x_padding, pady=default_y_padding)

# Instructions for use
description_label.grid(row=1, rowspan=12, column=0, padx=default_x_padding, pady=default_y_padding)

row_padding_4.grid(row=10, column=2, pady=dedicated_padding_y)

# Place special button widgets
format_button.grid(row=11, column=2, padx=default_x_padding, pady=default_y_padding)
exit_button.grid(row=12, column=2, pady=15, padx=5)


# ===== Loop to sustain window

# Infinite loop to update tk window and check for conditions to activate or deactivate buttons
while True:
    recipName = enter_name_box.get()  # Get var from entry widget

    # Get name of zip file and display it in label widget
    truncatedInputZip = inputZip.split("/")[-1]
    selected_zip_var.set(f"Selected: {truncatedInputZip}")

        if startExportFlag:
            format_button.config(state="disabled")
            startExportFlag = False
            begin_export_thread.join()

    if inputZip and outputDir and recipName:
        format_button.config(state="normal")

    if startExportFlag:
        format_button.config(state="disabled")
        startExportFlag = False

    if finishExportFlag:
        inputZip = ""
        enter_name_box.delete(0, tk.END)  # Clear entry box
        format_button.config(state="normal")
        finishExportFlag = False

    root.update()
