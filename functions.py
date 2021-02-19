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

"""This module has the class and functions to format one WhatsApp chat in its entirety.

Classes:
    Message:
        The class for each message in a chat. Every instance is a separate message.

Functions:
    clean_html(string: str) -> str:
        Remove < and > to avoid rogue HTML tags.

    simple_format_to_html(string: str) -> str:
        Replace WhatsApp format characters with their HTML tags. Doesn't handle code blocks.

    complete_format_to_html(string: str) -> str:
        Replace WhatsApp format characters with their HTML tags. Handles code blocks.

    format_links(string: str) -> str:
        Find all the links in the string and put them in <a> tags.

    fully_format_message_content(string: str) -> str:
        Take message content and fully format it properly.

    add_attachments(attachment: str) -> str:
        Create HTML tags to embed attachments.

    write_text(chat_title: str, group_chat: bool):
        Format and write all text in _chat.txt to HTML file.

    move_attachment_files():
        Move all attachment files that don't need to be converted.

    extract_zip(input_file: str) -> bool:
        Extract the zip file given by file_dir into the temp directory. Return True if successfully extracted.

    fully_format_chat(group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
        Fully format an already exported chat.

    process_single_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
        Process a single chat completely. Extract and then fully format it.

    process_list(chat_list: list):
        Process a list of chats completely.

"""

from pydub import AudioSegment
from datetime import datetime
from zipfile import ZipFile
from shutil import copytree
from glob import glob
import threading
import re
import os

htmlAudioFormats = {'.mp3': 'mpeg', '.ogg': 'ogg', '.wav': 'wav'}  # Dict of HTML accepted audio formats
formatDict = {'_': 'em', '*': 'strong', '~': 'del'}  # Dict of format chars with their HTML tags

# Tuple of extensions that can be moved without being converted
nonConversionExtensions = ('jpg', 'png', 'webp', 'gif', 'mp4', 'mp3', 'ogg', 'wav')

cwd = os.getcwd()
senderName = htmlFileName = outputDir = ''

# RegEx patterns

fullPrefixPattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): ((.|\n)+)')
# Groups: full prefix is 1, time is 2, name is 3, content is 4

groupMetaPrefixPattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] (.+)')
# Groups: full prefix is 1, time is 2, content is 3

attachmentPattern = re.compile(r'<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$')
# Groups: filename without extension is 1, file type is 2, extension is 3

# Link pattern taken from urlregex.com
linkPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

encryptedMessagesNoticePattern = re.compile(
    r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): '
    r'Messages and calls are end-to-end encrypted\. No one outside of this chat, not even WhatsApp, can read or listen to them\.$')


class Message:
    """The class for each message in a chat. Every instance is a separate message.

    Methods:
        get_date():
            Return the date of the message.

        create_html() -> str:
            Return HTML representation of the Message object.

    """

    def __init__(self, original_string: str, group_chat: bool):
        """Create a Message object and fully format its content according to the type of message it is.

        Arguments:
            original_string:
                The complete original message including all prefix data.

            group_chat:
                A boolean to determine whether the message is from a group chat.

        """
        self._group_chat = group_chat
        original = original_string

        try:
            prefix_match = re.match(fullPrefixPattern, original)
            self._prefix = prefix_match.group(1)

            self._name = prefix_match.group(3)
            self._content = prefix_match.group(4)

            if re.match(attachmentPattern, self._content):
                self._content = add_attachments(self._content)
            else:
                self._content = fully_format_message_content(self._content)

            self._group_chat_meta = False

        except AttributeError:  # If no match was found for fullPrefixPattern, it's a group chat meta message
            prefix_match = re.match(groupMetaPrefixPattern, original)
            self._prefix = prefix_match.group(1)

            self._name = ''
            self._content = clean_html(prefix_match.group(3))

            self._group_chat_meta = True

        date_raw = prefix_match.group(1)
        time = prefix_match.group(2)

        # Use a ternary operator to get datetime object whether the message is in 12 hour or 24 hour format
        date_obj = datetime.strptime(date_raw, '%d/%m/%Y, %I:%M:%S %p') if ' am' in time or ' pm' in time \
            else datetime.strptime(date_raw, '%d/%m/%Y, %H:%M:%S')

        day = datetime.strftime(date_obj, '%d')
        if day.startswith('0'):
            day = day.replace('0', '', 1)  # Remove a single leading 0

        self._date = datetime.strftime(date_obj, f'%a {day} %B %Y')
        self._time = datetime.strftime(date_obj, '%I:%M:%S %p')

        if self._time.startswith('0'):
            self._time = self._time.replace('0', '', 1)

    def __repr__(self):
        """Return a repr of the Message object including the name, date, name, and whether it's from a group chat. Also includes the memory location in hex."""
        # Use hex here at end to give memory location of Message object
        if not self._group_chat_meta:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with name="{self._name}", ' \
                   f'date="{self._date}", time="{self._time}", and group_chat={self._group_chat} at {hex(id(self))}>'
        else:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with date="{self._date}", ' \
                   f'time="{self._time}", and group_chat={self._group_chat}, which is a meta message at ' \
                   f'{hex(id(self))}>'

    def get_date(self):
        """Return the date of the message."""
        return self._date

    def create_html(self) -> str:
        """Return HTML representation of the Message object."""
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
    """Remove < and > to avoid rogue HTML tags."""
    string = string.replace('<', '&lt;').replace('>', '&gt;')
    string = string.replace('\"', '&quot;').replace('\'', '&apos;')
    return string


def simple_format_to_html(string: str) -> str:
    """Replace WhatsApp format characters with their HTML tags. Doesn't handle code blocks."""
    first_tag = True
    list_string = list(string)

    for char, tag in formatDict.items():
        if char in string and string.count(char) % 2 == 0:
            for x, letter in enumerate(list_string):
                if letter == char:
                    if first_tag:
                        list_string[x] = f'<{tag}>'
                        first_tag = False
                    else:
                        list_string[x] = f'</{tag}>'
                        first_tag = True

    return ''.join(list_string)


def complete_format_to_html(string: str) -> str:
    """Replace WhatsApp format characters with their HTML tags. Handles code blocks."""
    first_tag = True
    if '```' in string:
        string = string.replace('```', '<code>')
        list_string = list(string)
        for x, letter in enumerate(list_string):
            if letter == '<':
                if first_tag:
                    first_tag = False
                else:
                    list_string[x] = '</'
                    first_tag = True

        string = ''.join(list_string)
    else:
        string = simple_format_to_html(string)

    return string


def format_links(string: str) -> str:
    """Find all the links in the string and put them in <a> tags."""
    # Get links and concat the RegEx groups into a list of links
    link_match_list = re.findall(linkPattern, string)
    link_matches = [''.join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            if re.match(r'[^A-Za-z]+(\.[^A-Za-z])+', link) and not re.match(r'(\d+\.){3}\d+', link):
                continue  # If not proper link but also not IP address, skip

            if not link.startswith('http'):
                working_link = f'http://{link}'  # Create URLs from non URL links
            else:
                working_link = link

            formatted_link = f'<a href="{working_link}" target="_blank">{link}</a>'
            string = string.replace(link, formatted_link)

    return string


def fully_format_message_content(string: str) -> str:
    """Take message content and fully format it properly.

    Clean the HTML of rogue tags, add HTML formatting tags for italics etc, create <a> tags for links, and add <br> tags.
    """
    string = clean_html(string)
    string = complete_format_to_html(string)
    string = format_links(string)
    string = string.replace('\n', '<br>\n\t\t')
    return string


def add_attachments(attachment: str) -> str:
    """Create HTML tags to embed attachments.

    It creates tags for images, videos, GIFs, and audio.
    This function automatically converts audio files when necessary, typically when they are .opus encoded voice messages.
    
    Arguments:
        attachment:
            The original, isolated attachment marker. Only the stuff between angled brackets.

    Returns:
        The HTML tag for the embedded attachment.

    """
    attachment_match = re.match(attachmentPattern, attachment)
    filename_no_extension = attachment_match.group(1)
    file_type = attachment_match.group(2)
    extension = attachment_match.group(3)

    filename = filename_no_extension + extension

    if file_type == 'AUDIO':
        for ext, html_format in htmlAudioFormats.items():
            if extension == ext:
                attachment = f'<audio controls>\n\t\t\t<source src="Attachments/{htmlFileName}/{filename}" ' \
                                  f'type="audio/{html_format}">\n\t\t</audio>'
                break

        else:  # If none of the standard HTML audio formats broke out of the for loop, convert to .mp3
            AudioSegment.from_file(f'temp/{filename}').export(
                f'temp/{filename_no_extension}.mp3', format='mp3')
            os.remove(f'temp/{filename}')
            filename = filename_no_extension + '.mp3'
            attachment = f'<audio controls>\n\t\t\t' \
                         f'<source src="Attachments/{htmlFileName}/{filename}" type="audio/mpeg">\n\t\t</audio>'
            os.rename(f'{cwd}/temp/{filename}', f'{outputDir}/Attachments/{htmlFileName}/{filename}')

    elif file_type == 'VIDEO':
        attachment = f'<video controls>\n\t\t\t<source src="Attachments/{htmlFileName}/{filename}">\n\t\t</video>'

    elif (file_type == 'PHOTO') or (file_type == 'GIF' and extension == '.gif') or (file_type == 'STICKER'):
        attachment = f'<img class="small" src="Attachments/{htmlFileName}/{filename}" alt="IMAGE ATTACHMENT" ' \
                          'style="max-height: 400px; max-width: 800px; display: inline-block;">'

    elif file_type == 'GIF' and extension != '.gif':  # Add gif as video that autoplays and loops like a proper gif
        attachment = f'<video autoplay loop muted playsinline>\n\t\t\t<source src="Attachments/{htmlFileName}/' \
                          f'{filename}">\n\t\t</video>'

    else:
        attachment = f'UNKNOWN ATTACHMENT "{filename}"'

    return attachment


def write_text(chat_title: str, group_chat: bool):
    """Format and write all text in _chat.txt to HTML file.

    This function creates a new HTML file with the global htmlFileName.
    If that filename already exist, it will be given a number in brackets at the end of the name.
    It only writes the text of _chat.txt to the HTML file.
    It should be in a thread running parallel with a thread running move_attachment_files().

    Arguments:
        chat_title:
            A string which becomes the title of the chat. Not the filename, but the title.

        group_chat:
            A boolean to determine whether the chat is a group chat.

    """
    date_separator = ''

    with open('temp/_chat.txt', encoding='utf-8') as f:
        # Read file and remove LRM, LRE, and PDF Unicode characters
        chat_txt = f.read().replace('\u200e', '').replace('\u202a', '').replace('\u202c', '')

    # Add number to end of file if the file already exists
    if not os.path.isfile(f'{outputDir}/{htmlFileName}.html'):
        html_file = open(f'{outputDir}/{htmlFileName}.html', 'w+', encoding='utf-8')
    else:
        same_name_number = 1
        while os.path.isfile(f'{outputDir}/{htmlFileName} ({same_name_number}).html'):
            same_name_number += 1
        html_file = open(f'{outputDir}/{htmlFileName} ({same_name_number}).html', 'w+', encoding='utf-8')

    with open('start_template.txt', encoding='utf-8') as f:
        start_template = f.readlines()  # f.readlines() preserves \n characters

    # Replace chat_title in start_template
    for i, line in enumerate(start_template):
        pos = line.find('%chat_title%')
        if pos != -1:  # If 'chat_title' is found
            start_template[i] = line.replace('%chat_title%', chat_title)

    for line in start_template:
        html_file.write(line)

    # Use a re.sub to place LRMs between each message and then create a list by splitting by LRM
    chat_txt = re.sub(r'\n\[(?=\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2})])', '\u200e[', chat_txt)
    chat_txt_list = chat_txt.split('\u200e')

    # ===== MAIN WRITE LOOP

    for string in chat_txt_list:
        # If it's the notice that messages are encrypted, skip it
        if re.match(encryptedMessagesNoticePattern, string):
            continue

        msg = Message(string, group_chat)

        if msg.get_date() != date_separator:
            date_separator = msg.get_date()
            html_file.write(f'<div class="date-separator">{date_separator}</div>\n\n')

        html_file.write(msg.create_html())

    with open('end_template.txt', encoding='utf-8') as f:
        end_template = f.readlines()

    for line in end_template:
        html_file.write(line)

    html_file.close()

    os.remove('temp/_chat.txt')


def move_attachment_files():
    """Move all attachment files that don't need to be converted.

    This function moves all attachment files that don't need to be converted to the global outputDir.
    It only moves the attachment files.
    It should be in a thread running parallel with a thread running write_text().
    """
    files = glob('temp/*')

    if files:
        for f in files:
            f = f.replace('\\', '/')
            filename = f.split('/')[-1]
            extension = filename.split('.')[-1]

            if extension in nonConversionExtensions:
                os.rename(f'{cwd}/temp/{filename}', f'{outputDir}/Attachments/{htmlFileName}/{filename}')


def extract_zip(input_file: str) -> bool:
    """Extract the zip file given by file_dir into the temp directory. Return True if successfully extracted.

    If input_file is not a valid zip file, it is skipped and the function returns False.

    This function must be called before fully_format_chat() to ensure correct operation.

    Arguments:
        input_file:
            The name of the original input zip file. It must end in '.zip'.

    Returns:
        True if the file is successfully extracted, but False if it isn't.

    """
    try:
        zip_file_object = ZipFile(input_file)
        zip_file_object.extractall('temp')
        zip_file_object.close()
        return True
    except OSError:
        print(f'ERROR: {input_file} was not found. Skipping.')
        return False


def fully_format_chat(group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
    """Fully format an already extracted chat.

    This function will format every message in _chat.txt and write it to output_dir/name.html.
    It will also move every attachment file to output_dir/Attachments/sender_name.

    extract_zip() must be called before this function to ensure correct operation.

    Arguments:
        group_chat:
            A boolean to determine whether the chat is a group chat.

        sender_name:
            The name of the sender in the chat. Typically the user's WhatsApp alias.

        chat_title:
            The title of the chat. This appears in the top bar and in the browser tab. It is not the file name.

        html_file_name:
            The intended name of the final HTML file.

        output_dir:
            The intended directory for the output. The HTML file, Attachments folder, and Library folder will go here.
    """
    global senderName, htmlFileName, outputDir

    senderName = sender_name
    htmlFileName, _ = os.path.splitext(html_file_name)  # Remove possible '.html' from the end of the file name
    outputDir = output_dir

    if not os.path.isdir(f'{outputDir}/Library'):
        copytree('Library', f'{outputDir}/Library')

    if not os.path.isdir(f'{outputDir}/Attachments'):
        os.mkdir(f'{outputDir}/Attachments')

    if not os.path.isdir(f'{outputDir}/Attachments/{htmlFileName}'):
        os.mkdir(f'{outputDir}/Attachments/{htmlFileName}')

    text_thread = threading.Thread(target=write_text, args=[chat_title, group_chat])
    file_move_thread = threading.Thread(target=move_attachment_files)
    text_thread.start()
    file_move_thread.start()
    text_thread.join()
    file_move_thread.join()


def process_single_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
    """Process a single chat completely. Extract it and then fully format it.

    Arguments:
        input_file:
            The original zip file of the exported chat. It must have '.zip' on the end.

        group_chat:
            A boolean to determine whether the chat is a group chat.

        sender_name:
            The name of the sender in the chat. Typically the user's WhatsApp alias.

        chat_title:
            The title of the chat. This appears in the top bar and in the browser tab. It is not the file name.

        html_file_name:
            The intended name of the final HTML file.

        output_dir:
            The intended directory for the output. The HTML file, Attachments folder, and Library folder will go here.

    Raises:
        OSError:
            If the zip file is not found.

    """
    if extract_zip(input_file):
        fully_format_chat(group_chat, sender_name, chat_title, html_file_name, output_dir)
    else:
        raise OSError(f'Zip file "{input_file}" not found')


def process_list(chat_list: list):
    """Process a list of chats completely.

    Arguments:
        chat_list:
            A list of lists. Each sublist must have 6 elements. These elements are the arguments to be passed to process_single_chat().
            chat_list should look like this:
                [[input_file, group_hat, sender_name, chat_title, html_file_name, output_dir],
                [input_file, group_hat, sender_name, chat_title, html_file_name, output_dir], ...]

    """
    for chat_data in chat_list:
        # Check if chat_data is the right length and then unpack its values to pass to process_single_chat()
        if len(chat_data) == 6:
            process_single_chat(*chat_data)
