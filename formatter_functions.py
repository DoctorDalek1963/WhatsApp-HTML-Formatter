# from whatsapp_formatter import recipName, outputDir
from pydub import AudioSegment
from datetime import datetime
import re
import os

audio_extensions = (".opus", ".m4a")  # List of accepted non-mp3 audio files
image_extensions = (".jpg", ".png", ".webp")  # List of accepted image extensions
format_dict = {"_": "em", "*": "strong", "~": "del"}  # Dict of format characters and their tags

cwd = os.getcwd()

recipName = outputDir = ""


def pass_vars(name, output):
    global recipName, outputDir
    recipName = name
    outputDir = output


def clean_html(string):  # Get rid of <> in non-attachment messages
    """Remove the characters \"<\" and \">\" in non-attachment messages."""
    string = string.replace("<", "&lt;")
    string = string.replace(">", "&gt;")

    return string


def replace_tags(string, char, tag):  # Replace char with tags in string
    """Replace selected format character with selected HTML tag."""
    count = 0
    list_message = list(string)

    # Search through each char in list_message and replace odds with <tag> and evens with </tag>
    for x, letter in enumerate(list_message):
        if letter == char:
            if count == 0:
                # Replace char 1 with <tag>
                list_message[x] = str(f"<{tag}>")
                count = 1
            else:
                # Replace char 2 with </tag>
                list_message[x] = str(f"</{tag}>")
                count = 0

    return "".join(list_message)


def reformat(string):
    """Replace format characters (by calling tag_replace()) and add formatted links."""

    # ===== Format italics, bold, and strikethrough if there's an even number of format chars

    count = 0

    # If code block, ignore other format chars
    if "```" in string:
        string = string.replace("```", "<code>")
        list_string = list(string)
        for x, letter in enumerate(list_string):
            if letter == "<":
                if count == 0:
                    count = 1
                else:
                    list_string[x] = "</"
                    count = 0
        string = "".join(list_string)
    else:
        for x, (char, tag) in enumerate(format_dict.items()):
            if char in string:
                if string.count(char) % 2 == 0:
                    string = replace_tags(string, char, tag)

    # ===== Format links

    link_match_list = re.findall(r"(https?://)?(\w{3,}\.)?(\S+\.\S+)", string)
    # Join all elements in each tuple together and put the tuples into a list
    link_matches = ["".join(match) for match in link_match_list]

    if link_matches:
        for link in link_matches:
            formatted_link = f"<a href=\"{link}\" target=\"_blank\">{link}</a>"
            string = string.replace(link, formatted_link)

    return string


def add_attachments(string):
    """Embed images, videos, and audio."""
    # Parse filename and extension with a RegEx
    attachment_match = re.search(r"<attached: ([^.]+)(\.\w+)>$", string)
    extension = attachment_match.group(2)
    filename = attachment_match.group(1) + extension

    string_start = string.split("<attached: ")[0]

    # ===== Format attachments
    if extension in audio_extensions:
        # Convert audio file to mp3
        AudioSegment.from_file(f"temp/{filename}").export(f"{outputDir}/{recipName}/{filename}", format="mp3")
        string = string_start + f"<audio src=\"{recipName}/{filename}\" controls></audio>"
        string = create_message_block(string)
        return string

    # Copy file & metadata to attachment dir
    os.rename(f"{cwd}/temp/{filename}", f"{outputDir}/{recipName}/{filename}")

    if extension == ".mp3":
        string = f"{string_start}<audio src=\"{recipName}/{filename}\" controls></audio>"

    elif extension == ".mp4":
        string = f"{string_start}<video controls>\n\t<source src=\"{recipName}/{filename}\"" + \
                 " type=\"video/mp4\"></source>\n</video>"

    elif extension in image_extensions:
        string = f"{string_start}<img src=\"{recipName}/{filename}\" alt=\"Image\" width=\"30%\" height=\"30%\">"

    string = create_message_block(string)

    return string


def create_message_block(string):
    """Format message into <div> block with appropriate class."""
    if string == "":
        return "<br>\n"

    list_message = list(string)

    if not (re.match(r"\[\d{2}/\d{2}/\d{4}, ", string)):  # If a continuation
        string = "<br>" + "".join(list_message) + "\n"
        return string

    del list_message[0]

    # ===== Parse date, time, and name with one RegEx

    # re.match is used because this RegEx must occur at the beginning of a string
    message_info_match = re.match(r"\[(\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} [ap]m)] (\w+): ", string)

    date_raw = message_info_match.group(1)
    name = message_info_match.group(2)

    # Reformat date and time to be more readable
    date_obj = datetime.strptime(date_raw, "%d/%m/%Y, %I:%M:%S %p")
    date = datetime.strftime(date_obj, "%a %d %B %Y")
    time = datetime.strftime(date_obj, "%I:%M:%S %p")

    string = string.split(": ")[1]

    # ===== Create message block

    if name == recipName:
        string = f"<div class=\"message recipient\">{string}"
    else:
        string = f"<div class=\"message sender\">{string}"

    string = f"</div>\n{string} <span class=\"message-info time\">{time}</span>"
    string = f"{string}<span class=\"message-info date\">{date}</span>"

    return string
