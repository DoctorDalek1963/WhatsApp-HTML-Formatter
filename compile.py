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

"""This module compiles the WhatsApp Formatter with pyinstaller in GUI or CLI format. GUI by default.

Functions:
    compile_formatter(gui=True):
        Compile the WhatsApp Formatter with pyinstaller according to the truthiness of the gui keyword argument. It's true by default.

"""

import shutil
import os
import subprocess


def compile_formatter(gui=True):
    """Compile the WhatsApp Formatter using pyinstaller.

    Keyword arguments:
        gui:
            A boolean which is true if not specified. If true, the function will compile the GUI, if false, it will compile the CLI version.
    """
    # Get filename from gui boolean
    filename = 'gui.py' if gui else 'cli.py'

    if os.path.isfile('WhatsApp_Formatter.zip'):
        os.remove('WhatsApp_Formatter.zip')

    # Create temporary directory to hold everything
    os.mkdir('compile_temp')

    # Copy dependencies to temporary directory
    shutil.copy('start_template.txt', 'compile_temp/')
    shutil.copy('end_template.txt', 'compile_temp/')
    shutil.copytree('Library', 'compile_temp/Library')
    shutil.copy('release_readme.md', 'compile_temp/README.md')

    # Remove jsconfig file, which only exists on my machine
    if os.path.isfile('compile_temp/Library/jsconfig.json'):
        os.remove('compile_temp/Library/jsconfig.json')

    # Run pyinstaller with correct flags from the shell
    subprocess.call(f'pyinstaller {filename} -wF -n WhatsApp_Formatter --distpath ./compile_temp -i Library/favicon.ico', shell=True)

    # Remove spec file (I don't think there's a flag to tell pyinstaller to not generate this)
    os.remove('WhatsApp_Formatter.spec')

    # Zip up compiled program with dependencies
    shutil.make_archive('WhatsApp_Formatter', 'zip', 'compile_temp')

    # Clear and remove unnecessary directories
    shutil.rmtree('build')
    shutil.rmtree('compile_temp')
    if os.path.isdir('__pycache__'):
        shutil.rmtree('__pycache__')


if __name__ == '__main__':
    compile_formatter()
