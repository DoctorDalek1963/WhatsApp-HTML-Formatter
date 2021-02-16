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


class FormatterGUI(QMainWindow):
    def __init__(self):
        super(FormatterGUI, self).__init__()

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

        # ===== Create widgets

        self._instructions_label = QtWidgets.QLabel(self)
        self._instructions_label.setText(self._instructions_text)
        self._instructions_label.setAlignment(QtCore.Qt.AlignCenter)

        # ===== Arrange widgets properly

        self._vbox = QVBoxLayout()
        self._hbox = QHBoxLayout()
        self._arrange_widgets()

        self._central_widget = QWidget()
        self._central_widget.setLayout(self._hbox)
        self.setCentralWidget(self._central_widget)

    def _arrange_widgets(self):
        self._hbox.addWidget(self._instructions_label)
        # The margins are around the edges of the window and the spacing is between widgets
        self.setContentsMargins(10, 10, 10, 10)
        self._vbox.setSpacing(20)

        self._hbox.addLayout(self._vbox)


def show_window():
    app = QApplication(sys.argv)
    window = FormatterGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show_window()
