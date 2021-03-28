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

    Chat:
        The class for each chat to be formatted. Every instance is a separate chat.

Functions:
    process_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str) -> None:
        Process one chat completely.

    process_list_of_chats(list_of_chats: list) -> list:
        Fully format a list of lists, where each sub-list is a set of arguments to be passed to process_chat().

        Returns a list of all the sub-lists that couldn't be processed properly.

"""

import concurrent.futures
from datetime import datetime
import os
from pydub import AudioSegment
import re
import threading
import shutil
import zipfile


class Message:
    """The class for each message in a chat. Every instance is a separate message.

    Methods:
        get_date():
            Return the date of the message.

        create_html(sender_name: str) -> str:
            Return HTML representation of the Message object.

    """

    html_audio_formats = {'.mp3': 'mpeg', '.ogg': 'ogg', '.wav': 'wav'}  # Dict of HTML accepted audio formats

    # This is a dictionary of patterns and replacement patterns for converting WhatsApp formatting to HTML tags
    format_dict = {re.compile(r'\b_([^_]+)_\b'): r'<em>\1</em>',
                   re.compile(r'\*\b([^*]+)\b\*'): r'<strong>\1</strong>',
                   re.compile(r'~\b([^~]+)\b~'): r'<del>\1</del>',
                   re.compile(r'```\b([^`]+)\b```'): r'<code>\1</code>'}

    # Tuple of extensions that can be moved without being converted
    non_conversion_extensions = ('jpg', 'png', 'webp', 'gif', 'mp4', 'mp3', 'ogg', 'wav')

    # RegEx patterns

    full_prefix_pattern = re.compile(
        r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): ((.|\n)+)')
    # Groups: full prefix is 1, time is 2, name is 3, content is 4

    group_meta_prefix_pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+)')
    # Groups: full prefix is 1, time is 2, content is 3

    attachment_message_pattern = re.compile(r'<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$')
    # Groups: filename without extension is 1, file type is 2, extension is 3

    # Link pattern taken from urlregex.com
    link_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    encrypted_messages_notice_pattern = re.compile(
        r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): '
        r'Messages and calls are end-to-end encrypted\. No one outside of this chat, not even WhatsApp, can read or listen to them\.$')

    def __init__(self, original_string: str, group_chat: bool, html_file_name: str):
        """Create a Message object.

        Arguments:
            original_string: str:
                The original full content of the message, including all the prefix data in square brackets.

            group_chat: bool:
                A boolean representing whether the message came from a group chat.

            html_file_name: str:
                The name of the final HTML file.

        """
        self._group_chat = group_chat
        self._html_file_name = html_file_name

        # Remove LRM, LRE, and PDF Unicode characters from original_string
        original = original_string.replace('\u200e', '').replace('\u202a', '').replace('\u202c', '')

        prefix_match = re.match(Message.full_prefix_pattern, original)

        if prefix_match:  # If it's a normal message
            self._name = prefix_match.group(3)
            self._message_content = prefix_match.group(4)

            if re.match(Message.attachment_message_pattern, self._message_content):
                self._format_attachment_message()
            else:
                self._clean_message_content()
                self._format_with_html_tags()
                self._format_links()

                self._message_content = self._message_content.replace('\n', '<br>\n\t\t')

            self._group_chat_meta = False
        else:  # If it's a group chat meta message
            prefix_match = re.match(Message.group_meta_prefix_pattern, original)

            self._name = ''
            self._message_content = prefix_match.group(3)
            self._clean_message_content()

            self._group_chat_meta = True

        date_raw = prefix_match.group(1)
        time = prefix_match.group(2)

        # Use a ternary operator to get datetime object whether the message is in 12 hour or 24 hour format
        self._datetime_obj = datetime.strptime(date_raw, '%d/%m/%Y, %I:%M:%S %p') if ' am' in time or ' pm' in time \
            else datetime.strptime(date_raw, '%d/%m/%Y, %H:%M:%S')

        day = str(self._datetime_obj.day)

        # Get day of the month extension
        if day.endswith('1') and day != '11':
            extension = 'st'
        elif day.endswith('2') and day != '12':
            extension = 'nd'
        elif day.endswith('3') and day != '13':
            extension = 'rd'
        else:
            extension = 'th'

        self._day = day + extension

        self.date = datetime.strftime(self._datetime_obj, f'%a {self._day} %B %Y')
        self._time = datetime.strftime(self._datetime_obj, '%I:%M:%S %p')

        if self._time.startswith('0'):
            self._time = self._time.replace('0', '', 1)

    def __repr__(self):
        """Return a __repr__ of the Message instance including the name, date, name, and whether it's from a group chat. Also includes the memory location in hex."""
        # Use hex here at end to give memory location of Message object
        if self._group_chat_meta:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with date="{self.date}", ' \
                   f'time="{self._time}", and group_chat={self._group_chat}, which is a meta message at ' \
                   f'{hex(id(self))}>'
        else:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object with name="{self._name}", ' \
                   f'date="{self.date}", time="{self._time}", and group_chat={self._group_chat} at {hex(id(self))}>'

    def _clean_message_content(self):
        """Replace < and > in self._message_content to avoid rogue HTML tags."""
        self._message_content = self._message_content.replace('<', '&lt;').replace('>', '&gt;')

    def _format_with_html_tags(self):
        """Replace WhatsApp format characters with their HTML tag equivalents in self._message_content."""
        for pattern, replacement in Message.format_dict.items():
            self._message_content = re.sub(pattern, replacement, self._message_content)

    def _format_links(self):
        """Find all the links in self._message_content and wrap them in <a> tags."""
        links = re.findall(Message.link_pattern, self._message_content)

        for link in links:
            # Get rid of punctuation or spaces at the end of the link
            while re.search(r'[\s.,!?]$', link):
                link = link[:-1]

            formatted_link = f'<a href="{link}" target="_blank">{link}</a>'
            self._message_content = self._message_content.replace(link, formatted_link)

    def _format_attachment_message(self):
        """Format an attachment message to properly link to the attachment with HTML tags."""
        match = re.match(Message.attachment_message_pattern, self._message_content)
        filename_no_ext = match.group(1)
        file_type = match.group(2)
        extension = match.group(3)

        filename = filename_no_ext + extension

        if file_type == 'AUDIO':
            for ext, given_format in Message.html_audio_formats.items():
                # If it's a standard, accepted extension, use that format
                if extension == ext:
                    html_format = given_format
                    break

            else:  # If none of the standard HTML audio formats broke out of the for loop, it will be converted to an mp3 file, so use that format
                html_format = 'mpeg'
                filename = filename_no_ext + '.mp3'

            self._message_content = f'<audio controls>\n\t\t\t<source ' \
                                    f'src="Attachments/{self._html_file_name}/{filename}" ' \
                                    f'type="audio/{html_format}">\n\t\t</audio>'

        elif file_type == 'VIDEO':
            self._message_content = f'<video controls>\n\t\t\t<source ' \
                                    f'src="Attachments/{self._html_file_name}/{filename}">\n\t\t</video>'

        elif (file_type == 'PHOTO') or (file_type == 'GIF' and extension == '.gif') or (file_type == 'STICKER'):
            self._message_content = f'<img class="small" src="Attachments/{self._html_file_name}/{filename}" ' \
                                    f'alt="IMAGE ATTACHMENT" style="max-height: 400px; max-width: 800px; display: inline-block;">'

        elif file_type == 'GIF' and extension != '.gif':  # Add gif as video that autoplays and loops like a proper gif
            self._message_content = f'<video autoplay loop muted playsinline>\n\t\t\t<source ' \
                                    f'src="Attachments/{self._html_file_name}/{filename}">\n\t\t</video>'

        else:
            self._message_content = f'UNKNOWN ATTACHMENT "{filename}"'

    def create_html(self, sender_name: str) -> str:
        """Return HTML representation of the Message object.

        Arguments:
            sender_name: str:
                The sender in the chat that this message is from.

        """
        if not self._group_chat_meta:
            if self._name == sender_name:
                sender_type = 'sender'
            else:
                sender_type = 'recipient'

            # If this is a group chat and this isn't the sender, add the recipient's name
            if self._group_chat and self._name != sender_name:
                css_formatted_name = self._name.replace('\u00a0', '-')  # Replace no-break space with dash
                recipient_name = f'<span class="recipient-name {css_formatted_name}">{self._name}</span>'
            else:
                recipient_name = ''

            return f'<div class="message {sender_type}">\n\t{recipient_name}\n\t<span class="message-info date">' \
                   f'{self.date}</span>\n\t\t<p>{self._message_content}</p>\n\t<span class="message-info time">' \
                   f'{self._time}</span>\n</div>\n\n'

        else:  # If a meta message in a group chat
            return f'<div class="group-chat-meta">\n\t<span class="message-info date">{self.date}</span>\n\t\t' \
                   f'<p>{self._message_content}</p>\n\t<span class="message-info time">{self._time}</span>\n</div>\n\n'


class Chat:
    """The class for each chat to be formatted. Every instance is a separate chat.

    Methods:
        format():
            Fully extract the zip file and format the chat.

    """

    attachment_file_pattern = re.compile(r'(\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)$')
    # Groups: filename without extension is 1, file type is 2, extension is 3

    def __init__(self, input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
        """Create a Chat object with instance attributes equal to the arguments passed.

        Arguments:
            input_file:
                The original zip file of the exported chat. It must have the '.zip' extension.

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
        self._input_file = input_file
        self._group_chat = group_chat
        self._sender_name = sender_name
        self._chat_title = chat_title
        self._html_file_name = html_file_name
        self._output_dir = output_dir

        # TODO: Use this unique temp directory name to allow for chat processing to be multithreaded
        # os.path.splitext()[0] is used to remove extensions
        self._temp_directory = f'temp_{os.path.splitext(self._input_file)[0]}_{self._chat_title}_' \
                               f'{os.path.splitext(self._html_file_name)[0]}'

        # Make directories if they don't exist
        if not os.path.isdir(library_path := os.path.join(self._output_dir, 'Library')):
            shutil.copytree('Library', library_path)

        if not os.path.isdir(attachments_path := os.path.join(self._output_dir, 'Attachments', self._html_file_name)):
            os.makedirs(attachments_path)

    def _extract_zip(self) -> bool:
        """Extract the zip file into a temporary directory.

        Extract the object's input_file into a unique temporary directory. If the extraction fails, the method returns False and skips the file.

        Returns:
            True if the zip file was successfully extracted, False if not.

        """
        try:
            with zipfile.ZipFile(self._input_file) as zip_file:
                zip_file.extractall(self._temp_directory)

            return True

        except OSError:  # If the zip file failed to extract
            print(f'ERROR: Failed to extract {self._input_file}. It likely does not exist. This chat will be skipped.')
            return False

    def _write_text(self):
        """Write the contents of temp/_chat.txt to the output directory."""
        with open(os.path.join(self._temp_directory, '_chat.txt'), 'r', encoding='utf-8') as f:
            # Read file and remove LRM, LRE, and PDF Unicode characters
            chat_txt = f.read().replace('\u200e', '').replace('\u202a', '').replace('\u202c', '')

        # Add number to the end of the filename if the file already exists
        html_filename_with_directory_no_ext = os.path.join(self._output_dir, self._html_file_name)
        if not os.path.isfile(html_filename_with_directory_no_ext + '.html'):
            html_file = open(html_filename_with_directory_no_ext + '.html', 'w+', encoding='utf-8')
        else:
            same_name_number = 1

            while os.path.isfile(html_filename_with_directory_no_ext + f' ({same_name_number}).html'):
                same_name_number += 1

            html_file = open(html_filename_with_directory_no_ext + f' ({same_name_number}).html', 'w+', encoding='utf-8')

        start_template = open('start_template.txt', 'r', encoding='utf-8').readlines()  # .readlines() preserves \n characters

        # Replace chat title in start template
        for line in start_template:
            if '%chat_title%' in line:
                line = line.replace('%chat_title%', self._chat_title)

            html_file.write(line)

        # Use a re.sub to place LRMs between each message and then create a list by splitting by LRM
        chat_txt = re.sub(r'\n\[(?=\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2})])', '\u200e[', chat_txt)
        chat_txt_list = chat_txt.split('\u200e')

        date_separator = ''

        # === Write every message

        for raw_message in chat_txt_list:
            # If it's the notice that messages are encrypted, skip it
            if re.match(Message.encrypted_messages_notice_pattern, raw_message):
                continue

            msg = Message(raw_message, self._group_chat)

            if msg.date != date_separator:
                date_separator = msg.date
                html_file.write(f'<div class="date-separator">{date_separator}</div>\n\n')

            html_file.write(msg.create_html(self._sender_name))

        end_template = open('end_template.txt', 'r', encoding='utf-8')

        for line in end_template:
            html_file.write(line)

        html_file.close()

        os.remove(os.path.join(self._temp_directory, '_chat.txt'))

    def _move_attachment_files(self):
        """Move the attachment files in temp to the output directory."""
        files = os.listdir(self._temp_directory)
        for f in files:
            try:
                # Get the file type and the name without an extension
                file_type = re.match(Chat.attachment_file_pattern, f).group(2)
                f_no_ext = os.path.splitext(f)[0]

                if file_type == 'AUDIO':
                    # Convert audio files that can't be played in browsers with simple HTML audio tags
                    # This is necessary because all voice messages are .opus, which must be converted
                    if file_type not in Message.html_audio_formats.keys():
                        # Convert old audio file into .mp3 in same directory
                        AudioSegment.from_file(os.path.join(self._temp_directory, f)).export(
                            os.path.join(self._temp_directory, f_no_ext) + '.mp3', format='mp3')

                        # Remove old audio file
                        os.remove(os.path.join(self._temp_directory, f))
                        # Set f to new file to make moving the new file easier
                        f = f_no_ext + '.mp3'
            except AttributeError:  # File is named weird and doesn't match the RegEx
                pass

            os.rename(os.path.join(self._temp_directory, f), os.path.join(self._output_dir, 'Attachments', f))

    def _start_formatting_threads(self):
        """Start two threads to fully format the chat after it's been extracted."""
        self._write_text_thread = threading.Thread(target=self._write_text)
        self._move_attachment_files_thread = threading.Thread(target=self._move_attachment_files)

        self._write_text_thread.start()
        self._move_attachment_files_thread.start()

    def format(self):
        """Fully extract the zip file and format the chat."""
        self._extract_zip()
        self._start_formatting_threads()

        # Wait until directory is empty, then rmdir it
        while len(os.listdir(self._temp_directory)) > 0:
            pass

        os.rmdir(self._temp_directory)


def process_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str) -> None:
    """Process one chat completely.

    This function also checks that all arguments are of the right type before using them. If they're not, raise TypeError.

    Arguments:
        input_file: str:
            The original zip file of the exported chat. It must have '.zip' on the end.

        group_chat: bool:
            A boolean to determine whether the chat is a group chat.

        sender_name: str:
            The name of the sender in the chat. Typically the user's WhatsApp alias.

        chat_title: str:
            The title of the chat. This appears in the top bar and in the browser tab. It is not the file name.

        html_file_name: str:
            The intended name of the final HTML file.

        output_dir: str:
            The intended directory for the output. The HTML file, Attachments folder, and Library folder will go here.

    Raises:
        TypeError:
            If the arguments aren't all of the correct type.

    """
    args = [input_file, group_chat, sender_name, chat_title, html_file_name, output_dir]

    arg_types = [type(x) for x in args]
    printable_arg_types = '[' + ', '.join([str(x)[8:-2] for x in arg_types]) + ']'

    required_types = [str, bool, str, str, str, str]
    printable_required_types = '[' + ', '.join([str(x)[8:-2] for x in required_types]) + ']'

    # If all the arguments are of the correct type, format the chat
    if arg_types == required_types:
        chat = Chat(*args)
        chat.format()
    else:
        raise TypeError(f'Expected arg types of {printable_required_types}. Got {printable_arg_types} instead.')


def process_list_of_chats(list_of_chats: list) -> list:
    """Fully format a list of lists, where each sub-list is a list of arguments to be passed to process_chat().

    Returns:
        rejected_chats:
            A list of all the sub-lists that couldn't be processed properly. It is an empty list if no sub-lists failed.

    """
    rejected_chats = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a dictionary with the Future object of the method call as the key and the list of args as the value
        # This allows us to return the args of the rejected chats
        futures = {executor.submit(process_chat, *chat_data): chat_data for chat_data in list_of_chats}

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except TypeError:
                # Get the value from the dictionary using the Future object as the key
                # This is the arguments passed
                rejected_chats.append(futures[future])

    return rejected_chats
