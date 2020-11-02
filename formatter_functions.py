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

htmlAudioFormats = {".mp3": "mpeg", ".ogg": "ogg", ".wav": "wav"}  # Dict of html accepted audio formats
formatDict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format chars with their html tags

cwd = os.getcwd()
recipientName = outputDir = ""

# RegEx patterns
prefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): (.+)?")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$")
linkPattern = re.compile(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)")


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
        self.date = datetime.strftime(date_obj, "%a %d %B %Y")
        self.time = datetime.strftime(date_obj, "%I:%M:%S %p")

        if self.time.startswith("0"):
            self.time = self.time.replace("0", "", 1)

    def __repr__(self):
        return f'<Message object with name="{self.name}", date="{self.date}", and time="{self.time}">'

    def create_html(self) -> str:
        """Create HTML code from Message object."""
        if self.name == recipientName:
            start_string = f'<div class="message recipient">'
        else:
            start_string = f'<div class="message sender">'

        return f'{start_string}\n<span class="message-info time">{self.time}</span>' + \
               f'\n<span class="message-info date">{self.date}</span>\n\t{self.content}\n</div>\n\n'


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
    string = string.replace("\n", "<br>\n\t")
    return string


def add_attachments(message_content: str) -> str:
    """Embed images, videos, GIFs, and audios."""
    attachment_match = re.match(attachmentPattern, message_content)
    filename_no_extension = attachment_match.group(1)
    file_type = attachment_match.group(2)
    extension = attachment_match.group(3)

    filename = filename_no_extension + extension

    if file_type == "AUDIO":
        for _, tup in enumerate(htmlAudioFormats.items()):
            ext = tup[0]
            html_format = tup[1]
            if extension == ext:
                message_content = f'<audio controls>\n\t' + \
                                  f'<source src="{recipientName}/{filename}" type="audio/{html_format}">\n</audio>'
                break

        else:  # If none of the standard html audio formats broke out of the for loop, convert to .mp3
            # Convert audio file to .mp3
            AudioSegment.from_file(f"temp/{filename}").export(
                f"temp/{filename_no_extension}.mp3", format="mp3")
            os.remove(f"temp/{filename}")
            filename = filename_no_extension + ".mp3"
            message_content = f'<audio controls>\n\t' + \
                              f'<source src="{recipientName}/{filename}" type="audio/mpeg">\n</audio>'

    elif file_type == "VIDEO":
        message_content = f'<video controls>\n\t<source src="{recipientName}/{filename}">\n</video>'

    elif file_type == "PHOTO" or "GIF":
        message_content = f'<img src="{recipientName}/{filename}" alt="Image" width="30%" height="30%">'
    else:
        message_content = "UNKNOWN ATTACHMENT"

    # Move file to new directory
    os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipientName}/{filename}")

    return message_content


def extract_zip(file_dir: str):
    """MUST BE RUN BEFORE write_to_file().

    Extract the given zip file into the temp directory."""
    zip_file_object = ZipFile(file_dir)
    zip_file_object.extractall("temp")
    zip_file_object.close()


def write_to_file(name: str, output_dir: str):
    """MUST RUN extract_zip() FIRST.

    Go through _chat.txt, format every message, and write them all to output_dir/name.html."""
    global recipientName, outputDir
    recipientName = name
    outputDir = output_dir
    date_separator = ""

    if not os.path.isdir(f"{outputDir}/Library"):
        copytree("Library", f"{outputDir}/Library")

    if not os.path.isdir(f"{outputDir}/{recipientName}"):
        os.mkdir(f"{outputDir}/{recipientName}")

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
    chat_txt = re.sub(r"\n\[(?=\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m] \w+: )", "\n\u200e[", chat_txt)
    chat_txt_list = chat_txt.split("\u200e")

    # ===== MAIN WRITE LOOP

    for string in chat_txt_list:
        msg = Message(string)

        if msg.date != date_separator:
            date_separator = msg.date
            html_file.write(f'<div class="date-separator">{date_separator}</div>\n')

        html_file.write(msg.create_html())

    with open("end_template.txt", encoding="utf-8") as f:
        end_template = f.readlines()

    for line in end_template:
        html_file.write(line)

    html_file.close()

    os.remove("temp/_chat.txt")
    files = glob("temp/*")

    if files:  # Clear up any left over files (probably attachments with weird names)
        for f in files:
            os.remove(f)

    os.rmdir("temp")
