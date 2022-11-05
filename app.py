from flask import Flask, render_template, request, redirect, url_for
from flask_htpasswd import HtPasswdAuth
import os

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['SECRET_KEY'] = os.urandom(16)
htpasswd = HtPasswdAuth(app)

# @app.route('/')
# @htpasswd.required
# def index(user):
#     print(f"{user} has successfully logged in")
#     return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name))
    return tree

# https://gist.github.com/andik/e86a7007c2af97e50fbb
@app.route('/')
@htpasswd.required
def index(user):
    print(f"{user} has successfully logged in")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return render_template('index.html', tree=make_tree(path))

if __name__=="__main__":
    app.run(host='localhost', port=8888, debug=True)