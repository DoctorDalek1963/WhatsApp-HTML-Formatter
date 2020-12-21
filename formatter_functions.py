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
import threading
import re
import os

htmlAudioFormats = {".mp3": "mpeg", ".ogg": "ogg", ".wav": "wav"}  # Dict of html accepted audio formats
formatDict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format chars with their html tags

# Tuple of extensions that can be moved without being converted
nonConversionExtensions = ("jpg", "png", "webp", "gif", "mp4", "mp3", "ogg", "wav")

cwd = os.getcwd()
senderName = htmlFileName = outputDir = ""

# RegEx patterns
prefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): (.+)?")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$")
linkPattern = re.compile(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)(\.html?)?")


class Message:
    def __init__(self, original_string: str, group_chat_flag: bool):
        """Create a Message object.

It takes two arguments, a string representing the original message,
and a boolean representing whether it's a message from a group chat."""
        self.__group_chat = group_chat_flag

        original = original_string
        self.__prefix = re.match(prefixPattern, original).group(0)

        # Only split once to avoid breaking attachment messages
        self.__content = original.split(": ", 1)[1]

        if re.match(attachmentPattern, self.__content):
            self.__content = add_attachments(self.__content)
        else:
            self.__content = format_content(self.__content)

        message_info_match = re.match(prefixPattern, self.__prefix)

        date_raw = message_info_match.group(1)
        self.__name = message_info_match.group(2)

        # Reformat date and time to be more readable
        date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")

        day = datetime.strftime(date_obj, "%d")
        if day.startswith("0"):
            day = day.replace("0", "", 1)  # Remove a leading 0

        self.__date = datetime.strftime(date_obj, f"%a {day} %B %Y")
        self.__time = datetime.strftime(date_obj, "%I:%M:%S %p")

        if self.__time.startswith("0"):
            self.__time = self.__time.replace("0", "", 1)

    def __repr__(self):
        # Use hex here at end to give memory location of Message object
        return f'<{self.__class__.__module__}.{self.__class__.__name__} object with name="{self.__name}", ' \
               f'date="{self.__date}", and time="{self.__time}" at {hex(id(self))}>'

    def get_date(self):
        return self.__date

    def create_html(self) -> str:
        """Create HTML from Message object."""
        if self.__name == senderName:
            sender_type = 'sender'
        else:
            sender_type = 'recipient'

        # If this is a group chat and this isn't the sender, add the recipient's name
        if self.__group_chat and self.__name != senderName:
            css_formatted_name = '.' + self.__name.replace(' ', '-')
            recipient_name = f'<span class="recipient-name {css_formatted_name}">{self.__name}</span>\n\t'
        else:
            recipient_name = ''

        return f'<div class="message {sender_type}">\n\t{recipient_name}<span class="message-info time">{self.__time}' \
               f'</span>\n\t<span class="message-info date">{self.__date}</span>\n\t\t{self.__content}\n</div>\n\n'


def clean_html(string: str) -> str:
    """Remove <> to avoid rogue html tags."""
    string = string.replace("<", "&lt;").replace(">", "&gt;")
    string = string.replace('"', "&quot;").replace("'", "&apos;")
    return string


def format_to_html(string: str) -> str:
    """Replace format characters with their html tags."""
    first_tag = True
    list_string = list(string)

    for char, tag in formatDict.items():
        if char in string and string.count(char) % 2 == 0:
            for x, letter in enumerate(list_string):
                if letter == char:
                    if first_tag:
                        list_string[x] = f"<{tag}>"
                        first_tag = False
                    else:
                        list_string[x] = f"</{tag}>"
                        first_tag = True

    return "".join(list_string)


def replace_tags(string: str) -> str:
    """Replace format characters with html tags in string."""
    first_tag = True
    if "```" in string:
        string = string.replace("```", "<code>")
        list_string = list(string)
        for x, letter in enumerate(list_string):
            if letter == "<":
                if first_tag:
                    first_tag = False
                else:
                    list_string[x] = "</"
                    first_tag = True

        string = "".join(list_string)
    else:
        string = format_to_html(string)

    return string


def format_links(string: str) -> str:
    """Find links in message and put them in <a> tags."""
    # Get links and concat the RegEx groups into a list of links
    link_match_list = re.findall(linkPattern, string)
    link_matches = ["".join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            if re.match(r"[^A-Za-z]+(\.[^A-Za-z])+", link) and not re.match(r"(\d+\.){3}\d", link):
                continue  # If not proper link but also not IP address, skip

            if not link.startswith("http"):
                working_link = f"http://{link}"  # Create URLs from non URL links
            else:
                working_link = link

            formatted_link = f'<a href="{working_link}" target="_blank">{link}</a>'
            string = string.replace(link, formatted_link)

    return string


def format_content(string: str) -> str:
    """Take message content and format it properly."""
    string = clean_html(string)
    string = replace_tags(string)
    string = format_links(string)
    string = string.replace("\n", "<br>\n\t\t")
    return string


def add_attachments(message_content: str) -> str:
    """Embed images, videos, GIFs, and audios."""
    attachment_match = re.match(attachmentPattern, message_content)
    filename_no_extension = attachment_match.group(1)
    file_type = attachment_match.group(2)
    extension = attachment_match.group(3)

    filename = filename_no_extension + extension

    if file_type == "AUDIO":
        for ext, html_format in htmlAudioFormats.items():
            if extension == ext:
                message_content = f'<audio controls>\n\t\t\t<source src="Attachments/{htmlFileName}/{filename}" ' \
                                  f'type="audio/{html_format}">\n\t\t</audio>'
                break

        else:  # If none of the standard html audio formats broke out of the for loop, convert to .mp3
            AudioSegment.from_file(f"temp/{filename}").export(
                f"temp/{filename_no_extension}.mp3", format="mp3")
            os.remove(f"temp/{filename}")
            filename = filename_no_extension + ".mp3"
            message_content = f'<audio controls>\n\t\t\t' \
                              f'<source src="Attachments/{htmlFileName}/{filename}" type="audio/mpeg">\n\t\t</audio>'
            os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/Attachments/{htmlFileName}/{filename}")

    elif file_type == "VIDEO":
        message_content = f'<video controls>\n\t\t\t<source src="Attachments/{htmlFileName}/{filename}">\n\t\t</video>'

    elif file_type == "PHOTO" or "GIF":
        message_content = f'<img class="small" src="Attachments/{htmlFileName}/{filename}" alt="IMAGE ATTACHMENT" ' \
                           'style="max-height: 400px; max-width: 800px; display: inline-block;">'
    else:
        message_content = f'UNKNOWN ATTACHMENT "{filename}"'

    return message_content


def write_text(chat_title: str, group_chat: bool):
    """Write all text in _chat.txt to HTML file."""
    date_separator = ""

    with open("temp/_chat.txt", encoding="utf-8") as f:
        chat_txt = f.read().replace("\u200e", "")

    # Add number to end of file if the file already exists
    if not os.path.isfile(f"{outputDir}/{htmlFileName}.html"):
        html_file = open(f"{outputDir}/{htmlFileName}.html", "w+", encoding="utf-8")
    else:
        same_name_number = 1
        while os.path.isfile(f"{outputDir}/{htmlFileName} ({same_name_number}).html"):
            same_name_number += 1
        html_file = open(f"{outputDir}/{htmlFileName} ({same_name_number}).html", "w+", encoding="utf-8")

    with open("start_template.txt", encoding="utf-8") as f:
        start_template = f.readlines()  # f.readlines() preserves \n characters

    # Replace chat_title in start_template
    for i, line in enumerate(start_template):
        pos = line.find("%chat_title%")
        if pos != -1:  # If "chat_title" is found
            start_template[i] = line.replace("%chat_title%", chat_title)

    for line in start_template:
        html_file.write(line)

    # Use a re.sub to place LRMs between each message and then create a list by splitting by LRM
    chat_txt = re.sub(r"\n\[(?=\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m] \w+: )", "\u200e[", chat_txt)
    chat_txt_list = chat_txt.split("\u200e")

    # ===== MAIN WRITE LOOP

    for string in chat_txt_list:
        msg = Message(string, group_chat)

        if msg.get_date() != date_separator:
            date_separator = msg.get_date()
            html_file.write(f'<div class="date-separator">{date_separator}</div>\n\n')

        html_file.write(msg.create_html())

    with open("end_template.txt", encoding="utf-8") as f:
        end_template = f.readlines()

    for line in end_template:
        html_file.write(line)

    html_file.close()

    os.remove("temp/_chat.txt")


def move_attachment_files():
    """Move all attachment files that don't need to be converted.
This allows for multithreading."""
    files = glob("temp/*")

    if files:
        for f in files:
            f = f.replace("\\", "/")
            filename = f.split("/")[-1]
            extension = filename.split(".")[-1]

            if extension in nonConversionExtensions:
                os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/Attachments/{htmlFileName}/{filename}")


def extract_zip(file_dir: str):
    """MUST BE RUN BEFORE write_to_file().

Extract the given zip file into the temp directory."""
    try:
        zip_file_object = ZipFile(file_dir)
        zip_file_object.extractall("temp")
        zip_file_object.close()
        return True
    except OSError:
        print("ERROR: " + file_dir + " was not found. Skipping.")
        return False


def write_to_file(group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
    """MUST RUN extract_zip() FIRST.

Go through _chat.txt, format every message, and write them all to output_dir/name.html."""
    global senderName, htmlFileName, outputDir

    senderName = sender_name
    htmlFileName = html_file_name
    outputDir = output_dir

    if not os.path.isdir(f"{outputDir}/Library"):
        copytree("Library", f"{outputDir}/Library")

    if not os.path.isdir(f"{outputDir}/Attachments"):
        os.mkdir(f"{outputDir}/Attachments")

    if not os.path.isdir(f"{outputDir}/Attachments/{htmlFileName}"):
        os.mkdir(f"{outputDir}/Attachments/{htmlFileName}")

    text_thread = threading.Thread(target=write_text, args=[chat_title, group_chat])
    file_move_thread = threading.Thread(target=move_attachment_files)
    text_thread.start()
    file_move_thread.start()
    text_thread.join()
    file_move_thread.join()


def process_single_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str,
                        output_dir: str):
    """Process a single chat completely."""
    if extract_zip(input_file):
        write_to_file(group_chat, sender_name, chat_title, html_file_name, output_dir)


def process_list(chat_list: list):
    """RUN TO PROCESS MULTIPLE CHATS. PASSED AS A LIST OF LISTS.

chat_list is a list of lists.
Each list contains the input file, a group chat boolean, the sender name, the title of the chat,
the file name, and the output directory.

It should look like [[inputFile, groupChat, senderName, chatTitle, fileName, outputDir],
[inputFile, groupChat, senderName, chatTitle, fileName, outputDir],
[inputFile, groupChat, senderName, chatTitle, fileName, outputDir], ...]"""

    for chat_data in chat_list:
        process_single_chat(chat_data[0], chat_data[1], chat_data[2], chat_data[3], chat_data[4], chat_data[5])
