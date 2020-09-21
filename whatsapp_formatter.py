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
        inputFile = f"{inputFile}.zip"
    print()
    outputDir = input("Please enter a full output directory: ")
    print()
    recipName = input("Please enter the name of the recipient (case sensitive): ")
    print()

    print("Unzipping...")
    extract_zip(inputFile)
    print("Unzipped!")
    print()

    print("Reformatting...")

    write_to_file(recipName, outputDir)  # All the heavy lifting is done by this function

    print("Reformatting complete!")
    print()
    print("Process complete!")
    print()
    quitFlag = input("Type \'1\' to quit, press enter to continue with another zip... ")
