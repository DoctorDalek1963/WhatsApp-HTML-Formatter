import zipfile as zf
import os
import glob as g
import datetime as dt
import pydub as pd
import shutil

# ===== Initial Setup

# Debug bit
print()
print("Welcome to the WhatsApp Formatter!")
print()
print("Please move the selected zip to /venv/")
input_file = input("Please enter the name of the input zip file (including .zip extension): ")
print()

recipName = input("Please enter the name of the recipient (case sensitive): ")
print()
outputDir = input("Please enter a full output directory: ")
print()

# Extracts selected zip file to /Work Folder/
zip_ref = zf.ZipFile(input_file)
print("Unzipping...")
zip_ref.extractall("Work Folder")
zip_ref.close()
print("Unzipped!")
print()

# Make dir if it doesn't exist
try:
    os.mkdir("{output}/{name}".format(output=outputDir, name=recipName))
except OSError:
    pass

print("Reformatting...")

# Creates chat_txt as list of _chat.txt
with open("Work Folder/_chat.txt", encoding="utf-8") as f:
    chat_txt_list = f.read().splitlines()

extension_tuple = (".opus", ".m4a")  # List of accepted non-mp3 audio files


# ===== Define functions


def html_cleaner(string):  # Get rid of <> in non-attachment messages
    """Remove HTML tags."""
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
                list_message[x] = str("<{}>".format(tag))
                count = 1
            elif count == 1:
                # Replace char 2 with </tag>
                list_message[x] = str("</{}>".format(tag))
                count = 0

    return "".join(list_message)


def reformat(string):
    """Replace format characters (by calling tag_replace()) and add formatted links."""
    # ===== Format italics, bold, and strikethrough if there's an even number of format chars
    if "_" in string:
        if string.count("_") % 2 == 0:
            string = tag_replace(string, "_", "em")
    if "*" in string:
        if string.count("*") % 2 == 0:
            string = tag_replace(string, "*", "strong")
    if "~" in string:
        if string.count("~") % 2 == 0:
            string = tag_replace(string, "~", "del")

    # ===== Format links
    if "http" in string:
        # Find link
        offset = string.find("http")
        link_list = list(string)

        # Store piece of string before link and del it
        string_start = ""
        for x in range(offset):
            string_start = string_start + link_list[0]
            del link_list[0]
        string = "".join(link_list)

        # Get offset if there's text after link, else offset = len
        if " " in string:
            offset = string.find(" ")
        else:
            offset = len(string)

        # Store link and del it
        link = ""
        for x in range(offset):
            link = link + link_list[0]
            del link_list[0]
        string = "".join(link_list)

        # Store piece of string after link and del it
        string_end = ""
        for x in range(len(string)):
            string_end = string_end + link_list[0]
            del link_list[0]

        # Concat string back together
        link = "<a href=\"" + link + "\" target=\"_blank\">" + link + "</a>"
        string = string_start + link + string_end

    return string


def convert_audio(filename):
    """Convert all audio files to .mp3 to be used in HTML."""
    # Convert audio file to mp3
    pd.AudioSegment.from_file("Work Folder/{}".format(filename)).export(
        "{output}/{name}/{file}".format(output=outputDir, name=recipName, file=filename), format="mp3")
    return filename


def add_attachments(string):
    """Embed images, videos, and audio."""
    # Parse filename
    offset = string.find("<")
    list_string = list(string)
    string_start = "".join(list_string[0:offset])
    del list_string[0:offset + 11]
    del list_string[len(list_string) - 1]
    filename = "".join(list_string)
    list_filename = list(filename)

    # Parse extension
    offset = filename.find(".")
    extension = "".join(list_filename[offset:])

    # ===== Format attachments
    if extension in extension_tuple:
        filename = convert_audio(filename)
        string = string_start + \
            "<audio src=\"{name}/{file}\" controls></audio>".format(name=recipName, file=filename)
        string = create_message_block(string)
        return string

    # Copy file & metadata to attachment dir
    shutil.copy2("Work Folder/{}".format(filename),
                 "{output}/{name}/{file}".format(output=outputDir, name=recipName, file=filename))

    if extension == ".mp3":
        string = string_start + \
                 "<audio src=\"{name}/{file}\" controls></audio>".format(name=recipName, file=filename)

    elif extension == ".mp4":
        string = string_start + \
                 "<video controls>\n\t<source src=\"{name}/{file}\" type=\"video/mp4\"></source>\n</video>".format(
                     name=recipName, file=filename)

    elif extension == ".jpg" or ".png" or ".webp":
        string = string_start + "<img src=\"{name}/{file}\" alt=\"Image\" width=\"30%\" height=\"30%\">".format(
            name=recipName, file=filename)

    string = create_message_block(string)

    return string


def create_message_block(string):
    """Format message into <div> block with appropriate class."""
    if string == "":
        return "<br>\n"

    list_message = list(string)

    if list_message[0] != "[":  # If a continuation
        string = "<br>" + "".join(list_message) + "\n"
        return string

    del list_message[0]

    # ===== Parse date, time, and name

    # Parse date
    offset = string.find(",")
    date_raw = ""
    for x in range(offset - 1):
        date_raw = date_raw + list_message[0]
        del list_message[0]
    del list_message[0:2]
    string = "".join(list_message)

    # Reformat date
    date_obj = dt.datetime.strptime(date_raw, "%d/%m/%Y")
    date = dt.datetime.strftime(date_obj, "%a %d %B %Y")

    # Parse time
    offset = string.find("]")
    time = ""
    for x in range(offset):
        time = time + list_message[0]
        del list_message[0]
    del list_message[0:2]
    string = "".join(list_message)

    # Parse name
    offset = string.find(":")
    name = ""
    for x in range(0, offset):
        name = name + list_message[0]
        del list_message[0]
    del list_message[0:2]
    string = "".join(list_message)

    # ===== Create message block

    if name == recipName:
        string = "<div class=\"message recipient\">" + string
    else:
        string = "<div class=\"message sender\">" + string

    string = "</div>\n{string} <span class=\"message-info time\">{time}</span>".format(string=string, time=time)
    string = string + "<span class=\"message-info date\">{}</span>".format(date)

    return string


# ===== Reformat chat_txt into recipName.html

html_file = open("{output}/{name}.html".format(output=outputDir, name=recipName), "w+", encoding="utf-8")

with open("start_template.txt", encoding="utf-8") as f:
    start_template = f.readlines()

# Replace recipName in start_template
for i, line in enumerate(start_template):
    pos = line.find("%recipName%")
    if pos != -1:  # If "recipName" is found
        start_template[i] = line.replace("%recipName%", recipName)  # Replace with var

# Add start template
for i in start_template:
    html_file.write(i)

for i in chat_txt_list:
    # Detect attachments
    i = i.replace("\u200e", "")  # Clear left-to-right mark
    dst = i.find(": ")
    i_list = list(i)
    if i == "":
        pass
    else:
        if i.find("<attached:") != -1:  # If attachment
            if i_list[dst + 2] == "<":
                i = add_attachments(i)
                html_file.write(i)
                continue  # next i

    message = html_cleaner(i)
    message = reformat(message)  # Reformat message with tags
    message = create_message_block(message)  # Adds <div> tags with class="recipient" or "sender"
    html_file.write(message)

    # html_file.write(create_message_block(reformat(html_cleaner(i))))
    # Writes reformatted & complete message to recipName.html
    # USE THAT WHEN DONE

with open("end_template.txt", encoding="utf-8") as f:
    end_template = f.readlines()

# Add end template
for i in end_template:
    html_file.write(i)

# ===== Clear up Work Folder

# Deletes all files in /Work Folder
files = g.glob("Work Folder/*")
for f in files:
    os.remove(f)

print()
print("Process complete!")
