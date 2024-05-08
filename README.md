# kakusui-org
Source code for kakusui.org

## Requirements
python (runs on 3.11.8, lowest tested version is 3.11.4)

flask==3.0.3

waitress==3.0.0

python-dotenv==1.0.1

flask-cors==4.0.1

kairyou==1.6.1

ja-core-news-lg==3.7.0 (this is not a pip package, it is a spacy model) Must be installed via spacy.

## To build locally
1. Clone the repo, make sure you are using the production branch.
2. Navigate to the `src` directory. `cd src`
3. Run the setup script with the local argument. This will install all requirements and flag the environment as local. `python setup.py local`
4. Run the server. `python app.py` for a non-production server, or `python serve.py` for a production server.
5. Website will be on localhost:5000

## Contributing
If you would like to contribute, please open an issue or a pull request. No specific guidelines yet, but please be respectful and kind.