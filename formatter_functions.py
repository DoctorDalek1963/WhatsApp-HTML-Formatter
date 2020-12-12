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
recipientName = outputDir = ""

# RegEx patterns
prefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): (.+)?")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$")
linkPattern = re.compile(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)(\.html?)?")


class Message:
    def __init__(self, original_string: str):
        self.original = original_string
        self.prefix = re.match(prefixPattern, self.original).group(0)

        # Only split once to avoid breaking attachment messages
        self.content = self.original.split(": ", 1)[1]

        if re.match(attachmentPattern, self.content):
            self.content = add_attachments(self.content)
        else:
            self.content = format_content(self.content)

        message_info_match = re.match(prefixPattern, self.prefix)

        date_raw = message_info_match.group(1)
        self.name = message_info_match.group(2)

        # Reformat date and time to be more readable
        date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")

        day = datetime.strftime(date_obj, "%d")
        if day.startswith("0"):
            day = day.replace("0", "", 1)  # Remove a leading 0

        self.date = datetime.strftime(date_obj, f"%a {day} %B %Y")
        self.time = datetime.strftime(date_obj, "%I:%M:%S %p")

        if self.time.startswith("0"):
            self.time = self.time.replace("0", "", 1)

    def __repr__(self):
        # Use hex here at end to give memory location of Message object
        return f'<{self.__class__.__module__}.{self.__class__.__name__} object with name="{self.name}", ' + \
               f'date="{self.date}", and time="{self.time}" at {hex(id(self))}>'

    def create_html(self) -> str:
        """Create HTML code from Message object."""
        if self.name == recipientName:
            sender_type = 'recipient'
        else:
            sender_type = 'sender'

        return f'<div class="message {sender_type}">\n\t<span class="message-info time">{self.time}</span>\n\t' + \
               f'<span class="message-info date">{self.date}</span>\n\t\t{self.content}\n</div>\n\n'


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
            if re.match(r"\d+\.\d+", link):
                continue  # If decimal, ignore it

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
                message_content = f'<audio controls>\n\t\t\t' + \
                                  f'<source src="{recipientName}/{filename}" type="audio/{html_format}">\n\t\t</audio>'
                break

        else:  # If none of the standard html audio formats broke out of the for loop, convert to .mp3
            AudioSegment.from_file(f"temp/{filename}").export(
                f"temp/{filename_no_extension}.mp3", format="mp3")
            os.remove(f"temp/{filename}")
            filename = filename_no_extension + ".mp3"
            message_content = f'<audio controls>\n\t\t\t' + \
                              f'<source src="{recipientName}/{filename}" type="audio/mpeg">\n\t\t</audio>'
            os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipientName}/{filename}")

    elif file_type == "VIDEO":
        message_content = f'<video controls>\n\t\t\t<source src="{recipientName}/{filename}">\n\t\t</video>'

    elif file_type == "PHOTO" or "GIF":
        message_content = f'<img src="{recipientName}/{filename}" alt="IMAGE ATTACHMENT">'
    else:
        message_content = f'UNKNOWN ATTACHMENT "{filename}"'

    return message_content


def write_text():
    """Write all text in _chat.txt to HTML file.
Convert all non-recognised audio files and move them."""
    date_separator = ""

    with open("temp/_chat.txt", encoding="utf-8") as f:
        chat_txt = f.read().replace("\u200e", "")

    html_file = open(f"{outputDir}/{recipientName}.html", "w+", encoding="utf-8")

    with open("start_template.txt", encoding="utf-8") as f:
        start_template = f.readlines()  # f.readlines() preserves \n characters

    # Replace recipientName in start_template
    for i, line in enumerate(start_template):
        pos = line.find("%recipName%")
        if pos != -1:  # If "recipName" is found
            start_template[i] = line.replace("%recipName%", recipientName)

    for line in start_template:
        html_file.write(line)

    # Use a re.sub to place LRMs between each message and then create a list by splitting by LRM
    chat_txt = re.sub(r"\n\[(?=\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m] \w+: )", "\u200e[", chat_txt)
    chat_txt_list = chat_txt.split("\u200e")

    # ===== MAIN WRITE LOOP

    for string in chat_txt_list:
        msg = Message(string)

        if msg.date != date_separator:
            date_separator = msg.date
            html_file.write(f'<div class="date-separator">{date_separator}</div>\n\n')

        html_file.write(msg.create_html())

    with open("end_template.txt", encoding="utf-8") as f:
        end_template = f.readlines()

    for line in end_template:
        html_file.write(line)

    html_file.close()

    os.remove("temp/_chat.txt")
    # os.rmdir("temp")


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
                os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipientName}/{filename}")


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


def write_to_file(name: str, output_dir: str):
    """MUST RUN extract_zip() FIRST.

Go through _chat.txt, format every message, and write them all to output_dir/name.html."""
    global recipientName, outputDir
    recipientName = name
    outputDir = output_dir

    if not os.path.isdir(f"{outputDir}/Library"):
        copytree("Library", f"{outputDir}/Library")

    if not os.path.isdir(f"{outputDir}/{recipientName}"):
        os.mkdir(f"{outputDir}/{recipientName}")

    text_thread = threading.Thread(target=write_text)
    file_move_thread = threading.Thread(target=move_attachment_files)
    text_thread.start()
    file_move_thread.start()
    text_thread.join()
    file_move_thread.join()


def process_single_chat(input_file: str, name: str, output_dir: str):
    """Process a single chat completely."""
    if extract_zip(input_file):
        write_to_file(name, output_dir)


def process_list(chat_list: list):
    """RUN TO PROCESS MULTIPLE CHATS. PASSED AS A LIST OF LISTS.

chat_list is a list of lists.
Each list contains the input file, the recipient name, and the output directory.
It should look like [[inputFile, name, outputDir], [inputFile, name, outputDir], ...]"""
    for chat_data in chat_list:
        process_single_chat(chat_data[0], chat_data[1], chat_data[2])
