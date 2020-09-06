# import formatter_functions as ff
from formatter_functions import *
from zipfile import ZipFile
from glob import glob
import os
import re

# ===== Initial Setup

cwd = os.getcwd()

print("Welcome to the WhatsApp Formatter!")
print()
print(f"Please move the selected zip to {cwd}")
print()
input_file = input("Please enter the name of the input zip file: ")
if not input_file.endswith(".zip"):
    input_file = f"{input_file}.zip"
print()
recipName = input("Please enter the name of the recipient: ")
print()
outputDir = input("Please enter a full output directory: ")
print()

# Pass variables to formatter_functions.py to avoid circular imports
pass_vars(recipName, outputDir)

# Extracts selected zip file to /temp/
zip_file = ZipFile(input_file)
print("Unzipping...")
zip_file.extractall("temp")
zip_file.close()
print("Unzipped!")
print()

try:
    os.mkdir(f"{outputDir}/{recipName}")
except OSError:
    pass

# Creates chat_txt_list as list of _chat.txt
with open("temp/_chat.txt", encoding="utf-8") as f:
    chat_txt_list = f.read().splitlines()

print("Reformatting...")

# ===== Reformat chat_txt into recipName.html

html_file = open(f"{outputDir}/{recipName}.html", "w+", encoding="utf-8")

with open("start_template.txt", encoding="utf-8") as f:
    start_template = f.readlines()

# Replace recipName in start_template
for i, line in enumerate(start_template):
    pos = line.find("%recipName%")
    if pos != -1:  # If "recipName" is found
        start_template[i] = line.replace("{recipName}", recipName)  # Replace with var

# Add start template
for line in start_template:
    html_file.write(line)

for line in chat_txt_list:
    # Detect attachments
    line = line.replace("\u200e", "")  # Clear left-to-right mark
    distance = line.find(": ")
    line_list = list(line)

    if line == "":
        pass
    else:
        if re.search(r"<attached: ([^.]+)(\.\w+)>$", line):  # If attachment
            if line_list[distance + 2] == "<":
                line = add_attachments(line)
                html_file.write(line)
                continue  # next i

    # Write reformatted & complete message to {recipName}.html
    formatted_message = reformat(clean_html(line))
    html_file.write(create_message_block(formatted_message))

with open("end_template.txt", encoding="utf-8") as f:
    end_template = f.readlines()

# Add end template
for line in end_template:
    html_file.write(line)

print("Reformatting complete!")

# ===== Clear up /temp/

# Delete remaining files in /temp/ (should just be _chat.txt)
files = glob(f"temp/*")
for f in files:
    os.remove(f)

os.rmdir("temp")

print()
print("Process complete!")
print()
input("Press enter to exit the program...")
