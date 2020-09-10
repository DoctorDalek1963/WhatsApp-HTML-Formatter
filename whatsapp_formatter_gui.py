from tkinter import filedialog, StringVar
from formatter_functions import *
import tkinter as tk
import os

cwd = os.getcwd()
input_zip = outputDir = recipName = ""
finish_export_flag = start_export_flag = False

description_text = """Steps:\n
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
    global input_zip
    input_zip = filedialog.askopenfilename(initialdir=cwd, title="Select an exported chat",
                                           filetypes=[("Zip files", "*.zip")])


def select_output_dir():
    global outputDir
    outputDir = filedialog.askdirectory(initialdir="/", title="Select an output directory")


def begin_export():
    global start_export_flag, finish_export_flag
    start_export_flag = True
    extract_zip(input_zip)
    write_to_file(recipName, outputDir)
    finish_export_flag = True


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
description_label = tk.Label(root, text=description_text)

# Create special button widgets
format_button = tk.Button(root, text="Format", command=begin_export, state="disabled", bd=3)
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
    truncated_input_zip = input_zip.split("/")[-1]
    selected_zip_var.set(f"Selected: {truncated_input_zip}")

    # Display outputDir in label widget
    selected_output_var.set(f"Selected: \n{outputDir}")

    if input_zip and outputDir and recipName:
        format_button.config(state="normal")

    if start_export_flag:
        format_button.config(state="disabled")
        start_export_flag = False

    if finish_export_flag:
        input_zip = ""
        enter_name_box.delete(0, tk.END)  # Clear entry box
        format_button.config(state="normal")
        finish_export_flag = False

    root.update()
