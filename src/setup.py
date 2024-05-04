import sys
import subprocess

## Install python dependencies from requirements.txt
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

## Download the spacy model
subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'ja_core_news_lg'])

## If the script is called with the 'local' argument, create an empty file called 'local_flag'
## Local flag is used to indicate that the script is running in a local environment rather than it's cpanel hosting
if(len(sys.argv) > 1 and sys.argv[1] == 'local'):
    with open('local_flag', 'w') as f:
        pass