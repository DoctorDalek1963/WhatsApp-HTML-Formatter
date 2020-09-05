from pydub import AudioSegment
from datetime import datetime
from zipfile import ZipFile
from glob import glob
import tkinter
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

# Extracts selected zip file to /temp/
zip_ref = ZipFile(input_file)
print("Unzipping...")
zip_ref.extractall("temp")
zip_ref.close()
print("Unzipped!")
print()

# Make dir if it doesn't exist
try:
    os.mkdir(f"{outputDir}/{recipName}")
except OSError:
    pass

# Creates chat_txt_list as list of _chat.txt
with open("temp/_chat.txt", encoding="utf-8") as f:
    chat_txt_list = f.read().splitlines()

audio_extensions = (".opus", ".m4a")  # List of accepted non-mp3 audio files
image_extensions = (".jpg", ".png", ".webp")  # List of accepted image extensions
format_dict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format characters and their tags

print("Reformatting...")


# ===== Define functions


def html_cleaner(string):  # Get rid of <> in non-attachment messages
    """Remove the characters \"<\" and \">\" in non-attachment messages."""
    string = string.replace("<", "&lt;")
    string = string.replace(">", "&gt;")

    return string


def tag_replace(string, char, tag):  # Replace char with tags in string
    """Replace selected format character with selected HTML tag."""
    count = 0
    list_message = list(string)

    # Search through each char in list_message and replace odds with <tag> and evens with </tag>
    for x, letter in enumerate(list_message):
        if letter == char:
            if count == 0:
                # Replace char 1 with <tag>
                list_message[x] = str(f"<{tag}>")
                count = 1
            else:
                # Replace char 2 with </tag>
                list_message[x] = str(f"</{tag}>")
                count = 0

    return "".join(list_message)


def reformat(string):
    """Replace format characters (by calling tag_replace()) and add formatted links."""

    # ===== Format italics, bold, and strikethrough if there's an even number of format chars

    count = 0

    # If code block, ignore other format chars
    if "```" in string:
        string = string.replace("```", "<code>")
        list_string = list(string)
        for x, letter in enumerate(list_string):
            if letter == "<":
                if count == 0:
                    count = 1
                else:
                    list_string[x] = "</"
                    count = 0
        string = "".join(list_string)
    else:
        for x, (char, tag) in enumerate(format_dict.items()):
            if char in string:
                if string.count(char) % 2 == 0:
                    string = tag_replace(string, char, tag)

    # ===== Format links

    link_match_list = re.findall(r"(https?://)?(\w{3,}\.)?(\S+\.\S+)", string)
    # Join all elements in each tuple together and put the tuples into a list
    link_matches = ["".join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            formatted_link = f"<a href=\"{link}\" target=\"_blank\">{link}</a>"
            string = string.replace(link, formatted_link)

    return string


def add_attachments(string):
    """Embed images, videos, and audio."""
    # Parse filename and extension with a RegEx
    attachment_match = re.search(r"<attached: ([^\.]+)(\.\w+)>$", string)
    extension = attachment_match.group(2)
    filename = attachment_match.group(1) + extension

    string_start = string.split("<attached: ")[0]

    # ===== Format attachments
    if extension in audio_extensions:
        # Convert audio file to mp3
        AudioSegment.from_file(f"temp/{filename}").export(f"{outputDir}/{recipName}/{filename}", format="mp3")
        string = string_start + f"<audio src=\"{recipName}/{filename}\" controls></audio>"
        string = create_message_block(string)
        return string

    # Copy file & metadata to attachment dir
    os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipName}/{filename}")

    if extension == ".mp3":
        string = f"{string_start}<audio src=\"{recipName}/{filename}\" controls></audio>"

    elif extension == ".mp4":
        string = f"{string_start}<video controls>\n\t<source src=\"{recipName}/{filename}\"" + \
                 " type=\"video/mp4\"></source>\n</video>"

    elif extension in image_extensions:
        string = f"{string_start}<img src=\"{recipName}/{filename}\" alt=\"Image\" width=\"30%\" height=\"30%\">"

    string = create_message_block(string)

    return string


def create_message_block(string):
    """Format message into <div> block with appropriate class."""
    if string == "":
        return "<br>\n"

    list_message = list(string)

    if not (re.match(r"\[\d{2}/\d{2}/\d{4}, ", string)):  # If a continuation
        string = "<br>" + "".join(list_message) + "\n"
        return string

    del list_message[0]

    # ===== Parse date, time, and name with one RegEx

    # re.match is used because this RegEx must occur at the beginning of a string
    message_info_match = re.match(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): ", string)

    date_raw = message_info_match.group(1)
    name = message_info_match.group(2)

    # Reformat date and time to be more readable
    date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")
    date = datetime.strftime(date_obj, "%a %d %B %Y")
    time = datetime.strftime(date_obj, "%I:%M:%S %p")

    string = string.split(": ")[1]

    # ===== Create message block

    if name == recipName:
        string = f"<div class=\"message recipient\">{string}"
    else:
        string = f"<div class=\"message sender\">{string}"

    string = f"</div>\n{string} <span class=\"message-info time\">{time}</span>"
    string = f"{string}<span class=\"message-info date\">{date}</span>"

    return string


# ===== Reformat chat_txt into recipName.html

html_file = open(f"{outputDir}/{recipName}.html", "w+", encoding="utf-8")

with open("start_template.txt", encoding="utf-8") as f:
    start_template = f.readlines()

# Replace recipName in start_template
for i, line in enumerate(start_template):
    pos = line.find("{recipName}")
    if pos != -1:  # If "recipName" is found
        start_template[i] = line.replace("{recipName}", recipName)  # Replace with var

# Add start template
for i in start_template:
    html_file.write(i)

for i in chat_txt_list:
    # Detect attachments
    i = i.replace("\u200e", "")  # Clear left-to-right mark
    distance = i.find(": ")
    i_list = list(i)
    if i == "":
        pass
    else:
        if ": <attached: " in i:  # If attachment
            if i_list[distance + 2] == "<":
                i = add_attachments(i)
                html_file.write(i)
                continue  # next i

    # Write reformatted & complete message to {recipName}.html
    html_file.write(create_message_block(reformat(html_cleaner(i))))

with open("end_template.txt", encoding="utf-8") as f:
    end_template = f.readlines()

# Add end template
for i in end_template:
    html_file.write(i)

print("Reformatting complete!")

# ===== Clear up /temp/

# Delete remaining files in /temp/ (should just be _chat.txt)
files = glob("temp/*")
for f in files:
    os.remove(f)

os.rmdir("temp")

print()
print("Process complete!")
print()
input("Press enter to exit the program...")
