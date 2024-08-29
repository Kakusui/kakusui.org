## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import sys
import subprocess
import os

## Define the paths relative to the current working directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

FRONTEND_ENV = os.path.join(current_dir, "../frontend/.env")
BACKEND_ENV = os.path.join(current_dir, ".env")

##-------------------start-of-install_dependencies()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def install_dependencies() -> None:
   
    ## Install python dependencies from requirements.
    try:
        assert os.path.exists('requirements.txt')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

        print("Python dependencies installed successfully")

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

            print("Spacy model already downloaded")

        except:
            ## Download the spacy model

            print("Downloading spacy model...")

            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'ja_core_news_lg'])

            print("Spacy model downloaded successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except ImportError:
        print("Error: spacy library not found")
        sys.exit(1)

##-------------------start-of-setup_local_environment()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setup_local_environment() -> None:

    try:

        if(len(sys.argv) > 1 and sys.argv[1] == 'local'):

            print("Setting up local environment...")

            to_write_frontend = 'NODE_ENV=development\n'
            to_write_backend = 'V1_KAIRYOU_ROOT_KEY=test\nV1_EASYTL_ROOT_KEY=test\nV1_EASYTL_PUBLIC_API_KEY=test\nV1_ELUCIDATE_ROOT_KEY=test'
        else:

            print("Setting up production environment...")

            to_write_frontend = 'NODE_ENV=production\n'
            to_write_backend = ''
        
        os.makedirs(os.path.dirname(FRONTEND_ENV), exist_ok=True)

        with open(FRONTEND_ENV, 'w') as f:
            f.write(to_write_frontend)

        if(to_write_backend != ''):

            with open(BACKEND_ENV, 'w') as f:
                f.write(to_write_backend)

        print("Environment setup successfully")

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
