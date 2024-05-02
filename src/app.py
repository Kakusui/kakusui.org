import logging
from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)

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

## Routes

## Home Page
@app.route('/')
def home():
    app.logger.debug("Serving Home Page")
    return render_template('home.html')

## Okisouchi Pages
@app.route('/okisouchi/')
def okisouchi():
    app.logger.debug("Serving Okisouchi Page")
    return render_template('okisouchi/okisouchi.html')

@app.route('/okisouchi/tos/')
def tos():
    app.logger.debug("Serving TOS Page")
    return render_template('okisouchi/tos/tos.html')

@app.route('/okisouchi/privacypolicy/')
def privacy_policy():
    app.logger.debug("Serving Privacy Policy Page")
    return render_template('okisouchi/privacypolicy/privacypolicy.html')

## Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f"404 Error: {e}, Page Not Found")
    return render_template('/error_pages/404.shtml'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"500 Error: {e}, Internal Server Error")
    return render_template('/error_pages/500.shtml'), 500

@app.errorhandler(403)
def forbidden(e):
    app.logger.error(f"403 Error: {e}, Forbidden")
    return render_template('/error_pages/403.shtml'), 403

if(__name__ == '__main__'):
    app.run(debug=True)