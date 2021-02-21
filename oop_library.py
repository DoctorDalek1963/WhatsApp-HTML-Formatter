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

import re
import threading
from datetime import datetime


class Message:
    """The class for each message in a chat. Every instance is a separate message."""

    html_audio_formats = {'.mp3': 'mpeg', '.ogg': 'ogg', '.wav': 'wav'}  # Dict of HTML accepted audio formats
    format_dict = {'_': 'em', '*': 'strong', '~': 'del'}  # Dict of format chars with their HTML tags

    # Tuple of extensions that can be moved without being converted
    non_conversion_extensions = ('jpg', 'png', 'webp', 'gif', 'mp4', 'mp3', 'ogg', 'wav')

    # RegEx patterns

    full_prefix_pattern = re.compile(
        r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): ((.|\n)+)')
    # Groups: full prefix is 1, time is 2, name is 3, content is 4

    group_meta_prefix_pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] (.+)')
    # Groups: full prefix is 1, time is 2, content is 3

    attachment_pattern = re.compile(r'<attached: (\d{8}-(\w+)-\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})(\.\w+)>$')
    # Groups: filename without extension is 1, file type is 2, extension is 3

    # Link pattern taken from urlregex.com
    link_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    encrypted_messages_notice_pattern = re.compile(
        r'\[(\d{2}/\d{2}/\d{4}, (\d{1,2}:\d{2}:\d{2} [ap]m|\d{2}:\d{2}:\d{2}))] ([^:]+): '
        r'Messages and calls are end-to-end encrypted\. No one outside of this chat, not even WhatsApp, can read or listen to them\.$')

    def __init__(self, original_string: str, group_chat: bool):
        """Create a Message object."""
        self._group_chat = group_chat

        # Remove LRM, LRE, and PDF Unicode characters from original_string
        original = original_string.replace('\u200e', '').replace('\u202a', '').replace('\u202c', '')

        prefix_match = re.match(Message.full_prefix_pattern, original)

        if prefix_match:  # If it's a normal message
            self._name = prefix_match.group(3)
            self._message_content = prefix_match.group(4)

            if re.match(Message.attachment_pattern, self._message_content):
                pass  # TODO: Format self._message_content as an attachment
            else:
                pass  # TODO: Format self._message_content as a normal message

            self._group_chat_meta = False
        else:  # If it's a group chat meta message
            prefix_match = re.match(Message.group_meta_prefix_pattern, original)

            self._name = ''
            self._message_content = prefix_match.group(3)
            self._clean_message_content()

            self._group_chat_meta = True

        # Whichever pattern was matched, the prefix is group 1
        self._prefix = prefix_match.group(1)

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

    def _clean_message_content(self):
        """Replace < and > in self._message_content to avoid rogue HTML tags."""
        self._message_content = self._message_content.replace('<', '&lt;').replace('>', '&gt;')


class Chat:
    """The class for each chat to be formatted. Every instance is a separate chat.

    Methods:
        format():
            Fully extract the zip file and format the chat.
    """

    def __init__(self, input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
        """Create a Chat object with instance attributes equal to the arguments passed.

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

        """
        self._input_file = input_file
        self._group_chat = group_chat
        self._sender_name = sender_name
        self._chat_title = chat_title
        self._html_file_name = html_file_name
        self._output_dir = output_dir

    def _extract_zip(self):
        """Extract the zip file into the temp directory."""
        pass

    def _write_text(self):
        """Write the contents of temp/_chat.txt to the output directory."""
        pass

    def _move_attachment_files(self):
        """Move the attachment files in temp to the output directory."""
        pass

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
    required_types = [str, bool, str, str, str, str]

    # If all the arguments are of the correct type, format the chat
    if arg_types == required_types:
        chat = Chat(*args)
        chat.format()
    else:
        # I'm actually very proud of this code. If the arguments aren't all of the correct type, this TypeError gets raised
        # It gets just the string of the actual type for the type of every item in both lists and prints them nicely
        raise TypeError(f'Expected arg types of [{", ".join([str(x)[8:-2] for x in required_types])}]. '
                        f'Got [{", ".join([str(x)[8:-2] for x in arg_types])}] instead.')


def process_list_of_chats(list_of_chats: list) -> list:
    """Fully format a list of lists, where each sub-list is a set of arguments to be passed to process_chat().

    Returns:
        rejected_chats:
            A list of all the sub-lists that couldn't be processed properly. It is an empty list if no sub-lists failed.

    """
    rejected_chats = []

    for chat_data in list_of_chats:
        try:
            process_chat(*chat_data)
        except TypeError:
            # If the types in the sub-list are incorrect, add the sub-list to rejected_chats
            rejected_chats.append(chat_data)

    return rejected_chats
