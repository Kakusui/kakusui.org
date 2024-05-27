# kakusui-org
Source code for kakusui.org

## Prerequisites
python (runs on 3.11.8, lowest tested version is 3.11.4)
node 20.13.1
npm 10.8.0

## Python Requirements
flask==3.0.3

waitress==3.0.0

python-dotenv==1.0.1

flask-cors==4.0.1

kairyou==1.6.1

ja-core-news-lg==3.7.0 (this is not a pip package, it is a spacy model) Must be installed via spacy.

## Node Requirements
See `frontend/package.json` for a list of node requirements.

## To build locally
1. Clone the repo, make sure you are using the correct branch (currently `website-redesign`)
2. Navigate to the `src` directory. `cd src`. Inside is the python backend.
3. Run the setup script with the local argument. This will install all requirements and flag the environment as local. `python setup.py local`
4. Run the server. `python app.py` for a non-production server, or `python serve.py` for a production server.
5. Open a new terminal and navigate to the `frontend` directory. `cd frontend`. Inside is the react (vite) frontend.
6. First install all required packages, these are in `package.json`. Do `npm i`. Then run the dev server with `npm run dev`
7. | Note to self (frontend depends on a hardcoded .env file) You need to change this to be created dynamically based on setup.py (and see if we can get it to utilize the local_flag too)
8. Website will be on localhost:5173 (frontend) and localhost:5000 (backend)

## Contributing
If you would like to contribute, please open an issue or a pull request. No specific guidelines yet, but please be respectful.