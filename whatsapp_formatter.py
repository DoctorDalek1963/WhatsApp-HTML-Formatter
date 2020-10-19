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

from formatter_functions import write_to_file, extract_zip
import os

cwd = os.getcwd()
quitFlag = False

print("Welcome to the WhatsApp Formatter!")

while not quitFlag:
    print()
    print(f"Please move the selected zip to {cwd}")
    print()
    inputFile = input("Please enter the name of the input zip file: ")
    if not inputFile.endswith(".zip"):
        inputFile += ".zip"
    print()
    outputDir = input("Please enter a full output directory: ")
    print()
    recipName = input("Please enter the name of the recipient (case sensitive): ")
    print()

    try:
        print(f"Unzipping {inputFile}...")
        extract_zip(inputFile)
        print("Unzipped!")
    except OSError:
        print(f"{inputFile} not found")
        input("Press enter to exit")
        exit(0)

    print()

    print(f"Reformatting {inputFile}...")

    write_to_file(recipName, outputDir)  # All the heavy lifting is done by this function

    print("Reformatting complete!")
    print()
    print("Process complete!")
    print()
    quitFlag = input("Type \'1\' to quit, press enter to continue with another zip... ")
