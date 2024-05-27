## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import sys
import subprocess
import os
import secrets

##-------------------start-of-install_dependencies()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def install_dependencies() -> None:
   
    ## Install python dependencies from requirements.
    try:
        assert os.path.exists('requirements.txt')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except AssertionError:
        print("Error: requirements.txt file not found")
        sys.exit(1)

##-------------------start-of-download_spacy_model()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def download_spacy_model() -> None:

    try:
        ## Check if spacy is installed
        import spacy

        try:
            spacy.load("ja_core_news_lg")

        except:
            ## Download the spacy model
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'ja_core_news_lg'])

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except ImportError:
        print("Error: spacy library not found")
        sys.exit(1)

##-------------------start-of-setup_local_environment()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setup_local_environment() -> None:

    try:
        ## If the script is called with the 'local' argument, create an empty file called 'local_flag'
        ## Local flag is used to indicate that the script is running in a local environment rather than its cPanel hosting environment
        if(len(sys.argv) > 1 and sys.argv[1] == 'local'):
            with open('local_flag', 'w') as f:
                pass

        ## If local_flag exists, we need to create a .env file with a dummy ROOT_API_KEY value, so that the app can access its API locally (api.localhost:5000)
        ## Such a secret doesn't really matter in a local environment, but it's necessary for the app to run since the API is protected by an API key which is loaded from the environment.
        if(os.path.exists('local_flag') and not os.path.exists('.env')):
            with open('.env', 'w') as f:
                dummy_key = secrets.token_hex(16)
                f.write(f'ROOT_API_KEY={dummy_key}')

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

##-------------------start-of-main()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    install_dependencies()
    download_spacy_model()
    setup_local_environment()

if(__name__ == "__main__"):
    main()
