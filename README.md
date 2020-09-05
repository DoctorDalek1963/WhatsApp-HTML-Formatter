# WhatsApp-HTML-Formatter

A script to convert exported WhatsApp chats as zip files into formatted HTML files.

## Notices:
- **Please move the `WhatsApp-HTML-Formatter/Library` folder to the output directory**
- Feel free to change `WhatsApp-HTML-Formatter/Library/background-image.jpg` to whatever background image you'd like

## Dependencies:
- pydub ([http://pydub.com/])

## Steps:
1. Export the desired chat (must be a private chat; group chats don't work)
2. Run the Python script
3. Select the zip file from the file select dialog
4. Select an export directory from the dialog
5. Enter the name of the recipient (case sensitive)
6. The program will create a HTML file and a folder of attachments in the output directory and clean up the temporary files
7. Feel free to remove the original zip file
