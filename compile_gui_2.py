"""The second script to be run in the compile pipeline.

Zips up folder for release and cleans up."""

import shutil
import os

# Remove spec file (I don't think there's a flag to tell pyinstaller to not generate this)
os.remove('WhatsApp_Formatter.spec')

# Zip up compiled program with dependencies
shutil.make_archive('WhatsApp_Formatter', 'zip', 'compile_temp')

# Clear and remove unnecessary directories
shutil.rmtree('build')
shutil.rmtree('compile_temp')
shutil.rmtree('__pycache__')
