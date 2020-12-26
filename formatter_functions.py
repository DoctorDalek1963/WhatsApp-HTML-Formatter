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

htmlAudioFormats = {".mp3": "mpeg", ".ogg": "ogg", ".wav": "wav"}  # Dict of HTML accepted audio formats
formatDict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format chars with their HTML tags

# Tuple of extensions that can be moved without being converted
nonConversionExtensions = ("jpg", "png", "webp", "gif", "mp4", "mp3", "ogg", "wav")

cwd = os.getcwd()
senderName = htmlFileName = outputDir = ""

# RegEx patterns
fullPrefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] ([^:]+): ((.|\n)+)")
groupMetaPrefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (.+)")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$")
# Link pattern taken from urlregex.com
linkPattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


class Message:
    def __init__(self, original_string: str, group_chat_flag: bool):
        """Create a Message object.

It takes two arguments, a string representing the original message,
and a boolean representing whether it's a message from a group chat."""
        self._group_chat = group_chat_flag
        original = original_string

        try:
            self._prefix_match = re.match(fullPrefixPattern, original)
            self._prefix = self._prefix_match.group(1)

            self._name = self._prefix_match.group(2)
            self._content = self._prefix_match.group(3)

            if re.match(attachmentPattern, self._content):
                self._content = add_attachments(self._content)
            else:
                self._content = format_content(self._content)

            self._group_chat_meta = False

        except AttributeError:
            self._prefix_match = re.match(groupMetaPrefixPattern, original)
            self._prefix = self._prefix_match.group(1)

            self._name = ''
            self._content = clean_html(self._prefix_match.group(2))

            self._group_chat_meta = True

        date_raw = self._prefix_match.group(1)
        # Reformat date and time to be more readable
        date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")

        day = datetime.strftime(date_obj, "%d")
        if day.startswith("0"):
            day = day.replace("0", "", 1)  # Remove a leading 0

        self._date = datetime.strftime(date_obj, f"%a {day} %B %Y")
        self._time = datetime.strftime(date_obj, "%I:%M:%S %p")

        if self._time.startswith("0"):
            self._time = self._time.replace("0", "", 1)

    def __repr__(self):
        # Use hex here at end to give memory location of Message object
        if not self._group_chat_meta:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with name="{self._name}", ' \
                   f'date="{self._date}", time="{self._time}", and group_chat={self._group_chat} at {hex(id(self))}>'
        else:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with date="{self._date}", ' \
                   f'time="{self._time}", and group_chat={self._group_chat}, which is a meta message at ' \
                   f'{hex(id(self))}>'

    def get_date(self):
        return self._date

    def create_html(self) -> str:
        """Create HTML from Message object."""
        if not self._group_chat_meta:
            if self._name == senderName:
                sender_type = 'sender'
            else:
                sender_type = 'recipient'

            # If this is a group chat and this isn't the sender, add the recipient's name
            if self._group_chat and self._name != senderName:
                css_formatted_name = self._name.replace('\u00a0', '-')  # Replace no-break space with dash
                recipient_name = f'<span class="recipient-name {css_formatted_name}">{self._name}</span>'
            else:
                recipient_name = ''

            return f'<div class="message {sender_type}">\n\t{recipient_name}\n\t<span class="message-info date">' \
                   f'{self._date}</span>\n\t\t<p>{self._content}</p>\n\t<span class="message-info time">' \
                   f'{self._time}</span>\n</div>\n\n'

        else:  # If a meta message in a group chat
            return f'<div class="group-chat-meta">\n\t<span class="message-info date">{self._date}</span>\n\t\t' \
                   f'<p>{self._content}</p>\n\t<span class="message-info time">{self._time}</span>\n</div>\n\n'


def clean_html(string: str) -> str:
    """Remove <> to avoid rogue HTML tags."""
    string = string.replace("<", "&lt;").replace(">", "&gt;")
    string = string.replace('"', "&quot;").replace("'", "&apos;")
    return string


def format_to_html(string: str) -> str:
    """Replace format characters with their HTML tags."""
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
    """Replace format characters with HTML tags in string."""
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

        else:  # If none of the standard HTML audio formats broke out of the for loop, convert to .mp3
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
        # Read file and remove LRM, LRE, and PDF Unicode characters
        chat_txt = f.read().replace("\u200e", "").replace("\u202a", "").replace("\u202c", "")

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
    chat_txt = re.sub(r"\n\[(?=\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m])", "\u200e[", chat_txt)
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
    """Process a single chat completely.

This function takes six arguments. All except group_chat, which is a boolean, are strings.

- input_file is the original zip file of the exported chat ('.zip' is necessary)
- group_chat is True if the chat is a group chat and False if it's not
- sender_name is the name of the sender (your WhatsApp alias)
- chat_title is the title of the chat. This will be at the top of the page and in the title of the tab
- html_file_name is the name of the HTML file to be produced ('.html' should not be part of this)
- output_dir is the directory where the HTML file, Library directory, and Attachments directory should be generated"""

    if extract_zip(input_file):
        write_to_file(group_chat, sender_name, chat_title, html_file_name, output_dir)


def process_list(chat_list: list):
    """RUN TO PROCESS MULTIPLE CHATS. PASSED AS A LIST OF LISTS.

chat_list is a list of lists.
Each list contains the input file, a group chat boolean, the sender name, the title of the chat,
the file name, and the output directory.

It should look like this:
[[inputFile, groupChat, senderName, chatTitle, htmlFileName, outputDir],
[inputFile, groupChat, senderName, chatTitle, htmlFileName, outputDir],
[inputFile, groupChat, senderName, chatTitle, htmlFileName, outputDir], ...]"""

    for chat_data in chat_list:
        process_single_chat(chat_data[0], chat_data[1], chat_data[2], chat_data[3], chat_data[4], chat_data[5])
