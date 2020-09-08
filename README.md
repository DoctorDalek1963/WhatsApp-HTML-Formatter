# WhatsApp-Formatter

A script to convert WhatsApp chats exported as zip files into formatted HTML files.

## Notices:
- Feel free to change `WhatsApp-Formatter/Library/background-image.jpg` to whatever background image you'd like, just make sure it has the same name

## Dependencies:
- pydub (http://pydub.com/)

## Steps (Command Line):
1. Export the desired chat on your phone (must be a private chat; group chats don't work)
2. Run whatsapp_formatter.py
3. Enter the name of the zip file
4. Enter a full output directory
5. Enter the name of the recipient (case sensitive)
6. Wait until the program tells you that the process is complete

## Steps (GUI):
1. Export the desired chat on your phone (must be a private chat; group chats don't work)
2. Run whatsapp_formatter_gui.py
3. Select the zip file from the file selection dialog
4. Select an export directory from the directory selection dialog
5. Enter the name of the recipient (case sensitive)
6. Click the `Format` button
7. Wait until the `Exit` button is active and then click it to exit
