from formatter_functions import write_to_file
from zipfile import ZipFile
from glob import glob
import os

cwd = os.getcwd()

print("Welcome to the WhatsApp Formatter!")
print()
print(f"Please move the selected zip to {cwd}")
print()
input_file = input("Please enter the name of the input zip file: ")
if not input_file.endswith(".zip"):
    input_file = f"{input_file}.zip"
print()
outputDir = input("Please enter a full output directory: ")
print()
recipName = input("Please enter the name of the recipient: ")
print()

print("Unzipping...")

zip_file = ZipFile(input_file)
zip_file.extractall("temp")
zip_file.close()

print("Unzipped!")
print()

print("Reformatting...")

write_to_file(recipName, outputDir)  # All the heavy lifting is done by this function

print("Reformatting complete!")

files = glob("temp/*")
for f in files:
    os.remove(f)

os.rmdir("temp")

print()
print("Process complete!")
print()
input("Press enter to exit the program...")
