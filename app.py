from flask import Flask, render_template, request, flash, redirect, url_for
from flask_htpasswd import HtPasswdAuth
import os

app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['SECRET_KEY'] = os.urandom(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/new_project', methods = ['GET'])
@htpasswd.required
def new_project(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    projname = path + request.args.get('projname')
    if not os.path.exists(path=projname):
        os.mkdir(path=projname)
        os.chmod(path=projname, mode=0o2774)
    else:
        flash(f'The project with name {projname} already exists')
    return render_template('index.html', tree=make_tree(path))

# https://gist.github.com/andik/e86a7007c2af97e50fbb
@app.route('/')
@htpasswd.required
def index(user):
    print(f"{user} has successfully logged in")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return render_template('index.html', tree=make_tree(path))

if __name__=="__main__":
    app.run(host='localhost', port=8080, debug=True, use_reloader=True)