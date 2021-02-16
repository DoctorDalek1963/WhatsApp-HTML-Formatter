#!/usr/bin/env python

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

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget
import sys
import threading


class FormatterGUI(QMainWindow):
    def __init__(self):
        super(FormatterGUI, self).__init__()

        # A boolean to see if the window exists. Used to close properly
        self._exists = True

        self.setWindowTitle('WhatsApp Formatter')

        self._instructions_text = """Steps:\n\n
1. Select a single exported chat\n
2. Tick the box if the chat is a group chat\n
3. Enter the name of the sender (this is your WhatsApp alias)\n
4. Enter the desired title of the chat (the title that will appear at
the top of the page and in the tab title)\n
5. Enter the desired name of the HTML file ('.html' should not be present)\n
6. Select an output directory\n
7. Click the 'Add to list' button\n
8. Repeat steps 1-7 until you have selected all your chats\n
9. Click the 'Process all' button\n
10. Wait until the 'Processing...' text disappears
(This may take quite a while if you've selected several large chats)\n
11. Once the 'Exit' button is active, you can safely exit the program"""
        self._all_chats_list = []
        self._group_chat = False

        self._selected_chat = ''
        self._selected_output = ''

        self._sender_name = ''
        self._chat_title = ''
        self._filename = ''

        # ===== Create widgets

        self._instructions_label = QtWidgets.QLabel(self)
        self._instructions_label.setText(self._instructions_text)
        self._instructions_label.setAlignment(QtCore.Qt.AlignCenter)

        self._select_chat_button = QtWidgets.QPushButton(self)
        self._select_chat_button.setText('Select an exported chat')
        self._select_chat_button.clicked.connect(self._select_chat_dialog)

        self._selected_chat_label = QtWidgets.QLabel(self)
        self._selected_chat_label.setText('Selected: ')
        self._selected_chat_label.setAlignment(QtCore.Qt.AlignCenter)

        self._group_chat_checkbox = QtWidgets.QCheckBox(self)
        self._group_chat_checkbox.setText('Group chat')

        self._sender_name_label = QtWidgets.QLabel(self)
        self._sender_name_label.setText('Enter the name of the sender (your WhatsApp alias):')
        self._sender_name_label.setAlignment(QtCore.Qt.AlignCenter)

        self._sender_name_textbox = QtWidgets.QLineEdit(self)

        self._chat_title_label = QtWidgets.QLabel(self)
        self._chat_title_label.setText('Enter the desired title of the chat:')
        self._chat_title_label.setAlignment(QtCore.Qt.AlignCenter)

        self._chat_title_textbox = QtWidgets.QLineEdit(self)

        self._filename_label = QtWidgets.QLabel(self)
        self._filename_label.setText('Enter the desired name of the HTML file:')
        self._filename_label.setAlignment(QtCore.Qt.AlignCenter)

        self._filename_textbox = QtWidgets.QLineEdit(self)

        self._select_output_button = QtWidgets.QPushButton(self)
        self._select_output_button.setText('Select an output directory')
        # TODO: Connect _select_output_button

        self._selected_output_label = QtWidgets.QLabel(self)
        self._selected_output_label.setText('Selected: ')
        self._selected_output_label.setAlignment(QtCore.Qt.AlignCenter)

        self._add_to_list_button = QtWidgets.QPushButton(self)
        self._add_to_list_button.setText('Add to list')
        # TODO: Connect _add_to_list_button

        self._process_all_button = QtWidgets.QPushButton(self)
        self._process_all_button.setText('Process all')
        # TODO: Connect _process_all_button

        self._exit_button = QtWidgets.QPushButton(self)
        self._exit_button.setText('Exit')
        self._exit_button.clicked.connect(self._close_properly)

        # ===== Arrange widgets properly

        self._vbox = QVBoxLayout()
        self._hbox = QHBoxLayout()
        self._hbox_checkbox = QHBoxLayout()
        self._arrange_widgets()

        self._central_widget = QWidget()
        self._central_widget.setLayout(self._hbox)
        self.setCentralWidget(self._central_widget)

        # ===== Create threads

        self._get_textbox_values_thread = threading.Thread(target=self._loop_get_textbox_values)
        self._get_textbox_values_thread.start()

    def _arrange_widgets(self):
        self._hbox.addWidget(self._instructions_label)
        # The margins are around the edges of the window and the spacing is between widgets
        self.setContentsMargins(10, 10, 10, 10)
        self._hbox.setSpacing(20)

        self._vbox.addWidget(self._select_chat_button)
        self._vbox.addWidget(self._selected_chat_label)

        # Add spacing either side of the checkbox to center it
        self._hbox_checkbox.addStretch(1)
        self._hbox_checkbox.addWidget(self._group_chat_checkbox)
        self._hbox_checkbox.addStretch(1)
        self._vbox.addLayout(self._hbox_checkbox)

        self._vbox.addWidget(self._sender_name_label)
        self._vbox.addWidget(self._sender_name_textbox)
        self._vbox.addWidget(self._chat_title_label)
        self._vbox.addWidget(self._chat_title_textbox)
        self._vbox.addWidget(self._filename_label)
        self._vbox.addWidget(self._filename_textbox)
        self._vbox.addWidget(self._select_output_button)
        self._vbox.addWidget(self._selected_output_label)
        self._vbox.addWidget(self._add_to_list_button)
        self._vbox.addWidget(self._process_all_button)
        self._vbox.addWidget(self._exit_button)
        self._hbox.setSpacing(20)

        self._hbox.addLayout(self._vbox)

    def _select_chat_dialog(self):
        # This is a file select dialog to select a zip file
        self._selected_chat_raw = QtWidgets.QFileDialog.getOpenFileName(self, caption='Select an exported chat', filter='Zip files (*.zip)')

        # We then need to trim the raw data down into just the name of the zip file
        self._selected_chat = self._selected_chat_raw[0]
        self._selected_chat_display = self._selected_chat.split('/')[-1]

        self._selected_chat_label.setText(f'Selected: {self._selected_chat_display}')

    def _get_textbox_values(self):
        self._sender_name = self._sender_name_textbox.text()
        self._chat_title = self._chat_title_textbox.text()
        self._filename = self._filename_textbox.text()

    def _loop_get_textbox_values(self):
        while self._exists:
            self._get_textbox_values()

    def _close_properly(self):
        self.close()
        self._exists = False


def show_window():
    app = QApplication(sys.argv)
    window = FormatterGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show_window()
