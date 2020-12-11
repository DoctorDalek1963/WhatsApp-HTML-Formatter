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

from formatter_functions import process_list
import os
import re

cwd = os.getcwd()
processFlag = False

allChats = []  # List of all chat data lists to be processed

print("Welcome to the WhatsApp Formatter!")

while not processFlag:
    print()
    print(f"Please move the selected zip to {cwd}")
    print()
    inputFile = input("Please enter the name of the input zip file: ")
    if not inputFile.endswith(".zip"):
        inputFile += ".zip"
    print()
    output = input("Please enter a full output directory: ")
    print()
    name = input("Please enter the name of the recipient (case sensitive): ")
    print()

    allChats.append([inputFile, name, output])  # Add selected chat with data to allChats

    # Ask for another input
    processInput = input("Would you like to add another file (Y/n)? ")
    if re.match(r"[yY]", processInput):
        processFlag = False
    else:
        processFlag = True

# Process list of chats
print()
print("Processing all...")
process_list(allChats)
print("Processing complete!")
