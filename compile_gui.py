"""Fully compile the GUI version of the formatter with pyinstaller."""

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

# Run pyinstaller with correct flags from command prompt (I'm on Windows and haven't tested this on Linux or MacOS)
os.system('cmd /c "pyinstaller formatter_gui.py -wF -n WhatsApp_Formatter --distpath ./compile_temp -i '
          'Library/favicon.ico"')

# Remove spec file (I don't think there's a flag to tell pyinstaller to not generate this)
os.remove('WhatsApp_Formatter.spec')

# Zip up compiled program with dependencies
shutil.make_archive('WhatsApp_Formatter', 'zip', 'compile_temp')

# Clear and remove unnecessary directories
shutil.rmtree('build')
shutil.rmtree('compile_temp')
shutil.rmtree('__pycache__')
