import logging
from flask import Flask, render_template

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

## Routes

## Home Page

@app.route('/')
def home():
    app.logger.debug("Serving Home Page")
    return render_template('home.html')

## Okisouchi Pages

@app.route('/okisouchi')
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
    app.logger.error("Page Not Found" + str(e))
    app.logger.debug("Serving 404 Page")
    return render_template('/error_pages/404.shtml'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("Internal Server Error" + str(e))
    app.logger.debug("Serving 500 Page")
    return render_template('/error_pages/500.shtml'), 500

@app.errorhandler(403)
def forbidden(e):
    app.logger.error("Forbidden" + str(e))
    app.logger.debug("Serving 403 Page")
    return render_template('/error_pages/403.shtml'), 403

if(__name__ == '__main__'):
    app.run(debug=True)
