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

# Dict of html accepted audio formats
htmlAudioFormats = {".mp3": "mpeg", ".ogg": "ogg", ".wav": "wav"}
# Dict of format chars with their html tags
formatDict = {"_": "em", "*": "strong", "~": "del"}

cwd = os.getcwd()
recipientName = outputDir = ""

prefixPattern = re.compile(r"\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m] \w+: ")
attachmentPattern = re.compile(r"<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$") 


def clean_html(message: str):
    "Remove <> to avoid rogue html tags."
    message = message.replace("<", "&lt;").replace(">", "&gt;")
    message = message.replace("\"", "&quot;").replace("\'", "&apos;")
    return message


def format_to_html(message: str):
    "Replace format characters with their html tags."
    firstTag = True
    list_message = list(message)

    for char, tag in formatDict.items():
        for x, letter in enumerate(list_message):
            if letter == char:
                if firstTag:
                    list_message[x] = f"<{tag}>"
                    firstTag = False
                else:
                    list_message[x] = f"</{tag}>"
                    firstTag = True

    return "".join(list_message)


def replace_tags(message: str):
    "Replace format characters with html tags in message."
    list_message = list(message)
    firstTag = True

    if "```" in message:
        message = message.replace("```", "<code>")
        for x, letter in enumerate(list_message):
            if letter == "<":
                if firstTag:
                    firstTag = False
                else:
                    list_message[x] = "</"
                    firstTag = True 

        message = "".join(list_message)
    else:
        message = format_to_html(message) 

    return message


def format_links(message: str):
    "Find links in message and put them in <a> tags."
    # Get links and concat the RegEx groups into a list of links
    link_match_list = re.findall(r"(https?://)?(\w{3,}\.)?([^.\s]+\.[^.\s]+)", message)
    link_matches = ["".join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            if not link.startswith("http"):
                working_link = f"http://{link}"  # Create URLs from non URL links
            else:
                working_link = link

    formatted_link = f"<a href=\"{working_link}\" target=\"_blank\">{link}</a>"

    return message.replace(link, formatted_link)


def add_attachments(message: str):
    "Embed images, videos, GIFs, and audios."
    attachment_match = re.search(attachmentPattern, message)
    filename_no_extension = attachment_match.group(1)
    file_type = attachment_match.group(2)
    extension = attachment_match.group(3)

    filename = filename_no_extension + extension

    































