from flask import Flask, render_template, request
from flask_htpasswd import HtPasswdAuth

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
# app.config['FLASK_SECRET'] = 'Hey Hey Kids, secure me!'

htpasswd = HtPasswdAuth(app)


@app.route('/')
@htpasswd.required
def index(user):
    return 'Hello {user}'.format(user=user)

# @app.route("/")
# def index():
#     return render_template('index.html') 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
