# kakusui-org
Source code for kakusui.org

## Prerequisites
python (runs on 3.11.8, lowest tested version is 3.11.4)

node 20.13.1

npm 10.8.0

## Python Requirements
fastapi==0.111.0

gunicorn==22.0.0

uvicorn-worker==0.2.0

python-dotenv==1.0.1

kairyou==1.6.1

ja-core-news-lg==3.7.0 (this is not a pip package, it is a spacy model) Must be installed via spacy.

## Node Requirements
See `frontend/package.json` for a list of node requirements.

## To build locally
1. Clone the repo, make sure you are using the correct branch (currently `website-redesign`)
2. Navigate to the `backend` directory. `cd backend`. Inside is the python backend.
3. Run the setup script with the local argument. This will install all requirements and setup .env files. `python setup.py local`
4. Run the server. For local `uvicorn main:app --reload --port 5000` For production `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
5. Open a new terminal and navigate to the `frontend` directory. `cd frontend`. Inside is the react (vite) frontend.
6. First install all required packages, these are in `package.json`. Do `npm i`. Then run the dev server with `npm run dev`
7. Website will be on localhost:5173 (frontend) and localhost:5000 (backend)

## Frontend README
for development:

`npm i`

`npm run dev`

for production:

`npm i`

`npm run build`

When building for production make sure that `VITE_AUTHORIZATION` is set to the token for the api.

Ensure that `NODE_ENV`is set to `PRODUCTION`

## Contributing
If you would like to contribute, please open an issue or a pull request. No specific guidelines yet, but please be respectful.