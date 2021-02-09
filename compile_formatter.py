#!/usr/bin/env python

"""Fully compile the GUI version of the formatter with pyinstaller."""

import shutil
import os
import subprocess


def compile_formatter(gui=True):
    """Compile the WhatsApp Formatter using pyinsyaller.

This function takes one argument, gui, which is true by default. If it's true, this function will compile the GUI version of the formatter, if false, it will compile the command line version."""
    # Get filename from gui boolean
    filename = 'formatter_gui.py' if gui else 'formatter_cli.py'

    if os.path.isfile('WhatsApp_Formatter.zip'):
        os.remove('WhatsApp_Formatter.py')

    # Create temporary directory to hold everything
    os.mkdir('compile_temp')

    # Copy dependencies to temporary directory
    shutil.copy('start_template.txt', 'compile_temp/')
    shutil.copy('end_template.txt', 'compile_temp/')
    shutil.copytree('Library', 'compile_temp/Library')

    # Remove jsconfig file, which only exists on my machine
    if os.path.isfile('compile_temp/Library/jsconfig.json'):
        os.remove('compile_temp/Library/jsconfig.json')

    # Run pyinstaller with correct flags from the shell
    subprocess.call(f'pyinstaller {filename} -wF -n WhatsApp_Formatter --distpath ./compile_temp -i Library/favicon.ico', shell=True)

    # Remove spec file (I don't think there's a flag to tell pyinstaller to not generate this)
    os.remove('WhatsApp_Formatter.spec')

    # Zip up compiled program with dependencies
    shutil.make_archive('WhatsApp_Formatter', 'zip', 'compile_temp')

    # Clear and remove unnecessary directories
    shutil.rmtree('build')
    shutil.rmtree('compile_temp')
    if os.path.isdir('__pycache__'):
        shutil.rmtree('__pycache__')


if __name__ == '__main__':
    compile_formatter()
