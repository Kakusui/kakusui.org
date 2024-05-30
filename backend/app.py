## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
from logging.handlers import RotatingFileHandler

import os
import json
import logging

## third-party libraries
from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from kairyou import Kairyou
from kairyou.exceptions import InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound

##-------------------start-of-setup_app()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def setup_app(app:Flask) -> bool:

    ## Load Environment Variables
    load_dotenv()

    if(os.getenv('ENVIRONMENT') == 'development'):
        app.config['SERVER_NAME'] = 'localhost:5000'
        
    else:
        app.config['SERVER_NAME'] = 'kakusui.org'

    ## Store root API key
    app.config['ROOT_API_KEY'] = os.getenv('ROOT_API_KEY')

    ## Setup logging
    if(not os.path.exists('logs')):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/myapp.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application Startup')

##-------------------start-of-require_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## for now, as we don't want just anyone to access the API, we require root API key
def require_api_key(func):

    def decorated_function(*args, **kwargs):

        api_key = request.headers.get('Authorization')
        if(not api_key or api_key != f"{app.config['ROOT_API_KEY']}"):
            abort(401)  ## Unauthorized

        return func(*args, **kwargs)
    
    return decorated_function

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

## Setup the app
setup_app(app)

CORS(app, resources={r"/v1/*": {"origins": ["*"]}})

## Routes

## API Endpoints
@app.route('/', subdomain='api')
def api_home():
    return jsonify({"message": "Welcome to the API"})

@app.route('/v1/kairyou', subdomain='api', methods=["POST"])
@cross_origin(origins="*", headers=["Content-Type", "Authorization"])
@require_api_key
def kairyou():

    ## kairyou receives a POST request with a JSON payload (textToPreprocess) and (replacementsJson)
    ## it returns a JSON response with the preprocessed text, preprocessing log, and error log
    ## Possible status codes: 200, 400, 405, 500, 401
    ## 200: Success, 400: Missing required data, 405: Method not allowed, 500: Internal Server Error, 401: Unauthorized
    if(request.method == 'POST'):
        data:dict = request.get_json()

        text_to_preprocess = data.get('textToPreprocess')
        replacements_json = data.get('replacementsJson')

        if(not text_to_preprocess or not replacements_json):
            response = make_response(jsonify({"message": "Missing required data"}), 400)

        else:
            try:

                replacements_json = json.loads(replacements_json)

                preprocessed_text, preprocessing_log, error_log = Kairyou.preprocess(text_to_preprocess, replacements_json)

                response = make_response(jsonify({
                    "preprocessedText": preprocessed_text,
                    "preprocessingLog": preprocessing_log,
                    "errorLog": error_log
                }), 200)

            except (InvalidReplacementJsonKeys, InvalidReplacementJsonName):
                response = make_response(jsonify({"message": f"You have an invalid replacement json file. Please see https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#kairyou for usage."}), 400)
    
            except SpacyModelNotFound:
                response = make_response(jsonify({"message": "An internal error occurred. Please contact the administrator."}), 500)

    else:
        response = make_response(jsonify({"message": "This endpoint only accepts POST requests"}), 405)
    
    return response

## Under no circumstances should the app be run in production without a WSGI server
## EVER. This is only for development purposes.
## See: serve.py for production deployment.
if(__name__ == '__main__'):
    app.run(debug=True, port=5000)