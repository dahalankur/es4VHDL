from flask import Flask, render_template, request, redirect, url_for
from flask_htpasswd import HtPasswdAuth
import os

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['SECRET_KEY'] = os.urandom(16)
htpasswd = HtPasswdAuth(app)

@app.route('/')
@htpasswd.required
def index(user):
    print(f"{user} has successfully logged in")
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404