# WhatsApp-HTML-Formatter

 A script to convert exported WhatsApp chats as zip files into formatted HTML files.

## Notices:
Please make sure the working directory is set to `WhatsApp-HTML-Formatter/venv`

## Dependencies:
 pydub (![http://pydub.com/](http://pydub.com/))

## Steps:
 1. Export the desired chat (must be a private chat. Group chats don't work)
 2. Copy the zip file to the /venv/ folder
 3. Decide on an export directory and copy it
 4. Run the Python script and enter the name of the zip file, the name of the recipient (case sensitive), and the output directory
 5. The program will create a HTML file and a folder of attachments in the output directory and clean up the temporary files
 6. Remove the zip file
