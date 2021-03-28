# WhatsApp-Formatter

A program to convert WhatsApp chats exported as zip files into formatted HTML files for easier reading.

---

## Notices:
- **THIS ONLY WORKS FOR CHATS EXPORTED ON iOS**. As far as I'm aware, chats exported on Android use a completely different format. I've only tested this on LineageOS, though, so it might be fine if you exported the chat from a stock Android ROM.

- Feel free to change `Library/background-image.jpg` to whatever background image you'd like, just make sure it has the same name
- If you're formatting a group chat, please add the participants' names to `Library/group_chat_names.css` with colours, following the examples given at the top of the file

## Dependencies:
These are only necessary if you aren't on Windows and can't run `WhatsApp_Formatter.exe`. Install them with `pip install -r requirements.txt`.
- [pydub](https://pypi.org/project/pydub/)
- [PyQt5](https://pypi.org/project/PyQt5/)

---

## Steps:

1. Export the desired chat on your phone
2. Run gui.py or `WhatsApp_Formatter.exe` if you're on Windows
3. Select the first zip file with the `Select an exported chat` button
4. Tick the box if it's a group chat
5. Enter the name of the sender (your WhatsApp alias)
6. Enter the desired title of the chat
7. Enter the desired name of the output file
8. Select an output directory with the `Select an output directory` button
9. Click the `Add to list` button
10. Repeat steps 3-9 until you have selected all your chats
11. Click the `Process all` button to process and format all chats. (If there are many large zip files, this may take some time)
12. When all chats have been processed, the `Processing...` text will disappear, the `Exit` button will become enabled, and it will be safe to exit
