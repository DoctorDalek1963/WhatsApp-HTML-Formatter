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
# from zipfile import ZipFile
# from shutil import copytree
# from glob import glob
import re
import os

htmlAudioFormats = {".mp3": "mpeg", ".ogg": "ogg", ".wav": "wav"}  # Dict of html accepted audio formats
formatDict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format chars with their html tags

cwd = os.getcwd()
recipientName = outputDir = ""

# RegEx patterns
prefixPattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): ")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$") 
linkPattern = re.compile(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)")

# TODO: When parsing dates, add <div>s with date to separate days


class Message:
    def __init__(self, original_string: str):
        self.original = original_string.replace("\u200e", "")
        self.prefix = re.match(prefixPattern, self.original).group(0)
        self.content = self.original.split(": ")[1]

        if re.search(attachmentPattern, self.original):
            self.attachment = True
        else:
            self.attachment = False

    def __repr__(self):
        message_info_match = re.match(prefixPattern, self.original)

        date_raw = message_info_match.group(1)
        name = message_info_match.group(2)

        # Reformat date and time to be more readable
        date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")
        date = datetime.strftime(date_obj, "%a %d %B %Y")
        time = datetime.strftime(date_obj, "%I:%M:%S %p")

        if time.startswith("0"):
            time = time.replace("0", "", 1)

        if name == recipientName:
            start_string = f"<div class=\"message recipient\">"
        else:
            start_string = f"<div class=\"message sender\">"

        return f"{start_string}<span class=\"message-info time\">{time}</span>" + \
               f"<span class=\"message-info date\">{date}</span>\n\t{self.content}\n</div>"


def clean_html(string: str):
    """Remove <> to avoid rogue html tags."""
    string = string.replace("<", "&lt;").replace(">", "&gt;")
    string = string.replace("\"", "&quot;").replace("\'", "&apos;")
    return string


def format_to_html(string: str):
    """Replace format characters with their html tags."""
    first_tag = True
    list_string = list(string)

    for char, tag in formatDict.items():
        for x, letter in enumerate(list_string):
            if letter == char:
                if first_tag:
                    list_string[x] = f"<{tag}>"
                    first_tag = False
                else:
                    list_string[x] = f"</{tag}>"
                    first_tag = True

    return "".join(list_string)


def replace_tags(message: str):
    """Replace format characters with html tags in message."""
    first_tag = True
    if "```" in message:
        message = message.replace("```", "<code>")
        list_message = list(message)
        for x, letter in enumerate(list_message):
            if letter == "<":
                if first_tag:
                    first_tag = False
                else:
                    list_message[x] = "</"
                    first_tag = True

        message = "".join(list_message)
    else:
        message = format_to_html(message) 

    return message


def format_links(string: str):
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

            formatted_link = f"<a href=\"{working_link}\" target=\"_blank\">{link}</a>"
            string = string.replace(link, formatted_link)

        return string
    else:
        return string


def add_attachments(string: str):
    """Embed images, videos, GIFs, and audios."""
    attachment_match = re.search(attachmentPattern, string)
    filename_no_extension = attachment_match.group(1)
    file_type = attachment_match.group(2)
    extension = attachment_match.group(3)

    filename = filename_no_extension + extension

    message_prefix = re.match(prefixPattern, string).group(0)

    if file_type == "AUDIO":
        for ext, html_format in htmlAudioFormats:
            if extension == ext:
                string = f"{message_prefix}<audio controls>\n\t" + \
                         f"<source src=\"{recipientName}/{filename}\" type=\"audio/{html_format}\">\n</audio>"
                return string

        else:  # If none of the standard html audio formats broke out of the for loop, convert to .mp3
            # Convert audio file to .mp3
            AudioSegment.from_file(f"temp/{filename}").export(
                f"temp/{filename_no_extension}.mp3", format="mp3")
            string = f"{message_prefix}<audio controls>\n\t" + \
                     f"<source src=\"{recipientName}/{filename}\" type=\"audio/mpeg\">\n</audio>"

            return string

    elif file_type == "VIDEO":
        string = f"{message_prefix}<video controls>\n\t<source src=\"{recipientName}/{filename}\">\n</video>"

    elif file_type == "PHOTO" or "GIF":
        string = f"{message_prefix}<img src=\"{recipientName}/{filename}\" alt=\"Image\" width=\"30%\" height=\"30%\">"

    return string


#
