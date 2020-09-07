# WhatsApp-Formatter

A script to convert WhatsApp chats exported as zip files into formatted HTML files.

## Notices:
- **Please move the `WhatsApp-Formatter/Library` folder to the output directory**
- Feel free to change `WhatsApp-Formatter/Library/background-image.jpg` to whatever background image you'd like, just make sure it has the same name

## Dependencies:
- pydub ([http://pydub.com/])

## Steps (Command Line):
1. Export the desired chat (must be a private chat; group chats don't work)
2. Run whatsapp_formatter.py
3. Enter the name of the zip file
4. Enter a full output directory
5. Enter the name of the recipient (case sensitive)
6. The program will create a HTML file and a folder of attachments in the output directory and clean up the temporary files
7. Feel free to remove the original zip file

## Steps (GUI):
1. Export the desired chat (must be a private chat; group chats don't work)
2. Run whatsapp_formatter_gui.py
3. Select the zip file from the file select dialog
4. Select an export directory from the dialog
5. Enter the name of the recipient (case sensitive)
6. Click the `Format` button
7. Wait until the `Finish` button is active and then click it to exit
