from flask import Flask
from flask import render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trip', methods=['GET'])
def trip():
    if (request.args['location'] == '' or request.args['date'] == ''):
        return redirect(url_for('index'))
    return render_template('trip.html')
