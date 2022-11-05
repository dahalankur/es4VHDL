from flask import Flask
from flask_htpasswd import HtPasswdAuth

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '../.htaccess'
app.config['FLASK_SECRET'] = 'no secrets here!@#!@#' # TODO: get this from an env var later

htpasswd = HtPasswdAuth(app)

@app.route("/")
@htpasswd.required
def hello_world(user):
    return f"<p>Hello, {user}!</p>"


