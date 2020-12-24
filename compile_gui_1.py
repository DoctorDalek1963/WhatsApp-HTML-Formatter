"""The first script to be run in the compile pipeline.

Copies dependencies to folder and sets up stuff for pyinstaller to use."""

import shutil
import os

# Create temporary directory to hold everything
os.mkdir('compile_temp')

# Copy dependencies to temporary directory
shutil.copy('start_template.txt', 'compile_temp/')
shutil.copy('end_template.txt', 'compile_temp/')
shutil.copytree('Library', 'compile_temp/Library')

# Remove jsconfig file, which only exists on my machine
try:
    os.remove('compile_temp/Library/jsconfig.json')
except FileNotFoundError:
    pass
