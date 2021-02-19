#!/usr/bin/env python

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

"""This module simply contains a function to run the CLI version of the WhatsApp Formatter.

Functions:
    run_cli:
        Run the command line version of the WhatsApp Formatter.

"""

from functions import process_list
import shutil
import os
import re


def run_cli():
    """Run the command line version of the WhatsApp Formatter."""
    cwd = os.getcwd()
    process_flag = False

    all_chats = []  # List of all chat data lists to be processed

    print('Welcome to the WhatsApp Formatter!')

    while not process_flag:
        print()
        print(f'Please move the selected zip to {cwd}')
        print()

        input_file = input('Please enter the name of the input zip file: ')
        if not input_file.endswith('.zip'):
            input_file += '.zip'
        print()

        group_chat_raw_input = input('Is this a group chat? (Y/n) ')
        if re.match(r'[yY]', group_chat_raw_input):
            group_chat = True
        else:
            group_chat = False
        print()

        sender_name = input('Please enter the name of the sender (your WhatsApp alias): ')
        print()

        chat_title = input('Please enter the desired title of the chat: ')
        print()

        html_file_name = input('Please enter the desired name of the output file: ')
        print()

        output_dir = input('Please enter a full output directory: ')
        print()

        # Add selected chat with data to all_chats
        all_chats.append([input_file, group_chat, sender_name, chat_title, html_file_name, output_dir])

        # Ask for another input
        process_input = input('Would you like to add another file (Y/n)? ')
        if re.match(r'[yY]', process_input):
            process_flag = False
        else:
            process_flag = True

    # Process list of chats
    print()
    print('Processing all...')
    process_list(all_chats)
    shutil.rmtree('temp')
    print('Processing complete!')


if __name__ == "__main__":
    run_cli()
