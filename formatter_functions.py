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

from pydub import AudioSegment
from datetime import datetime
from zipfile import ZipFile
from shutil import copytree
from glob import glob
import re
import os

audioExtensions = (".opus", ".m4a")  # List of accepted non-mp3 audio files
imageExtensions = (".jpg", ".png", ".webp")  # List of accepted image extensions
formatDict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format characters and their tags

cwd = os.getcwd()
recipName = outputDir = ""
attachmentPattern = re.compile(r"\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m] \w+: <attached: ([^.]+)(\.\w+)>$")


def clean_html(string):  # Get rid of <> in non-attachment messages
    """Remove html entities in non-attachment messages."""
    string = string.replace("<", "&lt;").replace(">", "&gt;")
    string = string.replace("\"", "&quot;").replace("\'", "&apos;")

    return string


def replace_tags(string, char, tag):  # Replace char with tags in string
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
        for _, (char, tag) in enumerate(formatDict.items()):
            if char in string:
                if string.count(char) % 2 == 0:
                    string = replace_tags(string, char, tag)

    # ===== Format links

    link_match_list = re.findall(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)", string)
    # Join all elements in each tuple together and put the tuples into a list
    link_matches = ["".join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            if not link.startswith("http"):
                working_link = f"http://{link}"  # Create URLs from non URL links
                formatted_link = f"<a href=\"{working_link}\" target=\"_blank\">{link}</a>"
            else:
                formatted_link = f"<a href=\"{link}\" target=\"_blank\">{link}</a>"

            string = string.replace(link, formatted_link)

    return string


def add_attachments(string):
    """Embed images, videos, and audio."""
    # Parse filename and extension with a RegEx
    attachment_match = re.search(r"<attached: ([^.]+)(\.\w+)>$", string)
    extension = attachment_match.group(2)
    filename_no_extension = attachment_match.group(1)
    filename = filename_no_extension + extension

    string_start = string.split("<attached: ")[0]

    # ===== Format attachments
    if extension in audioExtensions:
        # Convert audio file to mp3
        AudioSegment.from_file(
            f"temp/{filename}").export(f"{outputDir}/{recipName}/{filename_no_extension}.mp3", format="mp3")
        string = string_start + f"<audio src=\"{recipName}/{filename_no_extension}.mp3\" controls></audio>"
        string = create_message_block(string)
        return string

    # Copy file & metadata to attachment dir
    os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipName}/{filename}")

    if extension == ".mp3":
        string = f"{string_start}<audio src=\"{recipName}/{filename}\" controls></audio>"

    elif extension == ".mp4":
        string = f"{string_start}<video controls>\n\t<source src=\"{recipName}/{filename}\"" + \
                 " type=\"video/mp4\"></source>\n</video>"

    elif extension in imageExtensions:
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

    if time.startswith("0"):
        time = time.replace("0", "", 1)

    string = string.split(": ")[1]

    # ===== Create message block

    if name == recipName:
        string = f"<div class=\"message recipient\">{string}"
    else:
        string = f"<div class=\"message sender\">{string}"

    string = f"</div>\n{string} <span class=\"message-info time\">{time}</span>"
    string = f"{string}<span class=\"message-info date\">{date}</span>"

    return string


def extract_zip(file):
    zip_file = ZipFile(file)
    zip_file.extractall("temp")
    zip_file.close()


def write_to_file(name, output):
    """Loop through every line of _chat.txt and write it to recipName.html with proper formatting."""
    global recipName, outputDir
    recipName = name
    outputDir = output

    if not os.path.isdir(f"{outputDir}/Library"):
        copytree("Library", f"{outputDir}/Library")

    if not os.path.isdir(f"{outputDir}/{recipName}"):
        os.mkdir(f"{outputDir}/{recipName}")

    # Creates chat_txt_list as list of _chat.txt
    with open("temp/_chat.txt", encoding="utf-8") as f:
        chat_txt_list = f.read().splitlines()

    # ===== Reformat chat_txt into recipName.html

    html_file = open(f"{outputDir}/{recipName}.html", "w+", encoding="utf-8")

    with open("start_template.txt", encoding="utf-8") as f:
        start_template = f.readlines()

    # Replace recipName in start_template
    for i, line in enumerate(start_template):
        pos = line.find("%recipName%")
        if pos != -1:  # If "recipName" is found
            start_template[i] = line.replace("%recipName%", recipName)  # Replace with var

    # Add start template
    for line in start_template:
        html_file.write(line)

    while len(chat_txt_list) > 0:
        line = chat_txt_list[0].replace("\u200e", "")
        del chat_txt_list[0]

        if re.match(attachmentPattern, line):
            line = add_attachments(line)
            html_file.write(line)
            continue  # Next line of chat

        # Write reformatted & complete message to recipName.html
        formatted_message = reformat(clean_html(line))
        html_file.write(create_message_block(formatted_message))

    with open("end_template.txt", encoding="utf-8") as f:
        end_template = f.readlines()

    # Add end template
    for line in end_template:
        html_file.write(line)

    html_file.close()

    files = glob("temp/*")
    for f in files:
        os.remove(f)

    os.rmdir("temp")
