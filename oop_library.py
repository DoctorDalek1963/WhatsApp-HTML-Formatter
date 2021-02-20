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
    process_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
        Process one chat completely.

"""

import re


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


class Chat:
    """The class for each chat to be formatted. Every instance is a separate chat."""

    sender_name = ''
    html_file_name = ''
    output_dir = ''

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

    def format(self):
        """Fully format the chat."""
        pass


def process_chat(input_file: str, group_chat: bool, sender_name: str, chat_title: str, html_file_name: str, output_dir: str):
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
                        f'Got [{", ".join([str(type(x))[8:-2] for x in args])}] instead.')
