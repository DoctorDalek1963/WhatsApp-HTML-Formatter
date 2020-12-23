"""The second script to be run in the compile pipeline.

Zips up folder for release and cleans up."""

import shutil
import os

os.remove('WhatsApp_Formatter.spec')

# Clear and remove the build director
shutil.rmtree('build')

# Zip up compiled program with dependencies
shutil.make_archive('WhatsApp_Formatter', 'zip', 'compile_temp')

# Clear and remove temporary directory
shutil.rmtree('compile_temp')
