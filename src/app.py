from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/okisouchi')
def okisouchi():
    return render_template('okisouchi/okisouchi.html')

@app.route('/okisouchi/tos/')
def tos():
    return render_template('okisouchi/tos/tos.html')

@app.route('/okisouchi/privacypolicy/')
def privacy_policy():
    return render_template('okisouchi/privacypolicy/privacypolicy.html')

## for development
if(__name__ == '__main__'):
    app.run(debug=True)
