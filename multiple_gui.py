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

from formatter_functions import process_list
from tkinter import filedialog, StringVar, IntVar
import tkinter as tk
import _tkinter
import threading
import os

cwd = os.getcwd()
inputFile = senderName = chatTitle = htmlFileName = outputDir = ''
startProcessingFlag = endProcessingFlag = addToListFlag = False
groupChat = False
allChatsList = []

descriptionText = """Steps:\n\n
1. Select a single exported chat\n
2. Tick the box if the chat is a group chat\n
3. Enter the name of the sender (this is your WhatsApp alias)\n
4. Enter the desired title of the chat (the title that will appear at
the top of the page and in the tab title)\n
5. Enter the desired name of the HTML file\n
6. Select an output directory\n
7. Click the 'Add to list' button\n
8. Repeat steps 1-7 until you have selected all your chats\n
9. Click the 'Process all' button\n
10. Wait until the 'Processing...' text disappears
(This may take quite a while if you've selected several large chats)\n
11. Once the 'Exit' button is active, you can safely exit the program"""

default_x_padding = 10
default_y_padding = 5
gap_y_padding = (5, 15)

# ===== Functions to be used on tk buttons


def select_zip():
    """Open a file dialog to select a zip file to use as input."""
    global inputFile
    inputFile = filedialog.askopenfilename(initialdir=cwd, title='Select an exported chat',
                                           filetypes=[('Zip files', '*.zip')])


def assign_group_chat_bool():
    """Handle updating the groupChat boolean variable from the tkinter checkbox."""
    global groupChat
    if group_chat_checkbox_var.get() == 1:
        groupChat = True
    else:
        groupChat = False


def select_output_dir():
    """Open a file dialog to select an output directory."""
    global outputDir
    outputDir = filedialog.askdirectory(initialdir='/', title='Select an output directory')


def add_to_list():
    """Add the current data to the list 'allChatsList' to be processed later."""
    global addToListFlag
    addToListFlag = True
    allChatsList.append([inputFile, groupChat, senderName, chatTitle, htmlFileName, outputDir])


def start_processing():
    """Set the 'startProcessingFlag' boolean to True."""
    global startProcessingFlag
    startProcessingFlag = True


def process_all_chats():
    """Process every chat in 'allChatsList' and then set the 'endProcessingFlag' boolean to True."""
    global endProcessingFlag
    process_list(allChatsList)
    endProcessingFlag = True


# ===== Tkinter initialisation

# Init window
root = tk.Tk()
root.title('WhatsApp Formatter')
root.resizable(False, False)
root.iconbitmap('Library/favicon.ico')

selected_zip_var = StringVar()
selected_output_var = StringVar()
processing_string_var = StringVar()

group_chat_checkbox_var = IntVar()


# ===== Create widgets

# Instructions for use
description_label = tk.Label(root, text=descriptionText)

# Create input widgets
select_zip_button = tk.Button(root, text='Select an exported chat', command=select_zip)
selected_zip_label = tk.Label(root, textvariable=selected_zip_var)

group_chat_checkbox = tk.Checkbutton(root, text='Group chat', variable=group_chat_checkbox_var,
                                     onvalue=1, offvalue=0, command=assign_group_chat_bool)

sender_name_box_label = tk.Label(root, text='Enter the name of the sender (your WhatsApp alias):')
enter_sender_name = tk.Entry(root)

chat_title_label = tk.Label(root, text='Enter the desired title of the chat:')
enter_chat_title = tk.Entry(root)

html_file_name_label = tk.Label(root, text='Enter the desired name of the HTML file:')
enter_html_file_name = tk.Entry(root)

select_output_button = tk.Button(root, text='Select an output directory', command=select_output_dir)
selected_output_label = tk.Label(root, textvariable=selected_output_var)

# Create special button widgets
add_to_list_button = tk.Button(root, text='Add to list', command=add_to_list, state='disabled', bd=3)
process_all_button = tk.Button(root, text='Process all', command=start_processing, state='disabled', bd=3)
processing_string_label = tk.Label(root, textvariable=processing_string_var)
exit_button = tk.Button(root, text='Exit', command=root.destroy, bd=3)


# ===== Place widgets

# Instructions for use
description_label.grid(row=1, rowspan=13, column=0, pady=15, padx=(default_x_padding, 50))

# Place input widgets
select_zip_button.grid(row=0, column=2, padx=default_x_padding, pady=(15, default_y_padding))
selected_zip_label.grid(row=1, column=2, padx=default_x_padding, pady=gap_y_padding)

group_chat_checkbox.grid(row=2, column=2, padx=default_x_padding, pady=gap_y_padding)

sender_name_box_label.grid(row=3, column=2, padx=default_x_padding, pady=default_y_padding)
enter_sender_name.grid(row=4, column=2, padx=default_x_padding, pady=gap_y_padding)

chat_title_label.grid(row=5, column=2, padx=default_x_padding, pady=default_y_padding)
enter_chat_title.grid(row=6, column=2, padx=default_x_padding, pady=gap_y_padding)

html_file_name_label.grid(row=7, column=2, padx=default_x_padding, pady=default_y_padding)
enter_html_file_name.grid(row=8, column=2, padx=default_x_padding, pady=gap_y_padding)

select_output_button.grid(row=9, column=2, padx=default_x_padding, pady=default_y_padding)
selected_output_label.grid(row=10, column=2, padx=default_x_padding, pady=(default_y_padding, 25))

# Place special button widgets
add_to_list_button.grid(row=11, column=2, padx=default_x_padding, pady=default_y_padding)
process_all_button.grid(row=12, column=2, padx=default_x_padding, pady=default_y_padding)
processing_string_label.grid(row=13, column=2, padx=default_x_padding, pady=default_y_padding)
exit_button.grid(row=14, column=2, padx=default_x_padding, pady=(default_y_padding, 15))


# ===== Loop to sustain window


def update_loop():
    """Infinite loop to continually update the root tkinter window and check for conditions
to activate/deactivate buttons."""
    global inputFile, senderName, chatTitle, htmlFileName, outputDir, allChatsList
    global startProcessingFlag, endProcessingFlag, addToListFlag

    while True:
        try:
            if enter_sender_name.get():
                senderName = enter_sender_name.get()

            if enter_chat_title.get():
                chatTitle = enter_chat_title.get()

            if enter_html_file_name.get():
                htmlFileName = enter_html_file_name.get()

            truncated_input_zip = inputFile.split('/')[-1]
            selected_zip_var.set(f'Selected: \n{truncated_input_zip}')

            selected_output_var.set(f'Selected: \n{outputDir}')

            if inputFile and senderName and chatTitle and htmlFileName and outputDir:
                add_to_list_button.config(state='normal')
            else:
                add_to_list_button.config(state='disabled')

            if addToListFlag:
                addToListFlag = False
                inputFile = ''
                group_chat_checkbox_var.set(0)  # Un-check group chat checkbox

                enter_sender_name.delete(0, tk.END)  # Clear entry box
                senderName = ''

                enter_chat_title.delete(0, tk.END)
                chatTitle = ''

                enter_html_file_name.delete(0, tk.END)
                htmlFileName = ''

            if allChatsList:
                process_all_button.config(state='normal')
            else:
                process_all_button.config(state='disabled')

            if startProcessingFlag:
                startProcessingFlag = False

                process_thread = threading.Thread(target=process_all_chats)
                process_thread.start()
                processing_string_var.set('Processing...')

                # Allow 'process all' button to be greyed out
                allChatsList = []

                # Clear all variables
                inputFile = ''
                group_chat_checkbox_var.set(0)  # Un-check group chat checkbox

                enter_sender_name.delete(0, tk.END)  # Clear entry box
                senderName = ''

                enter_chat_title.delete(0, tk.END)
                chatTitle = ''

                enter_html_file_name.delete(0, tk.END)
                htmlFileName = ''

                outputDir = ''

                select_zip_button.config(state='disabled')
                enter_sender_name.config(state='disabled')
                select_output_button.config(state='disabled')
                exit_button.config(state='disabled')

            if endProcessingFlag:
                processing_string_var.set('')

                select_zip_button.config(state='normal')
                enter_sender_name.config(state='normal')
                select_output_button.config(state='normal')
                exit_button.config(state='normal')

                endProcessingFlag = False

            root.update()

        except _tkinter.TclError:
            return


if __name__ == '__main__':
    update_loop()
