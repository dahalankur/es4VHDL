from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_htpasswd import HtPasswdAuth
import os

default_msg = '''
Welcome to ES4 VHDL online editor!

Begin by creating a new project, or selecting an existing one!
'''

# TODO: create a separate config file for all flask configs
app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['SECRET_KEY'] = os.urandom(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True

htpasswd = HtPasswdAuth(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[], path="")
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name, path=fn))
    return tree

# TODO: Update the size of the file tree and the editor window to be correct.


@app.route('/new_project', methods = ['GET'])
@htpasswd.required
def new_project(user):
    print("REQUESTED NEW PROJECT!")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    # flash("HIIII")
    # return render_template('index.html', tree=make_tree(path), file_contents="IEEE;")
    projname = path + request.args.get('projname')
    print(projname)
    if not os.path.exists(path=projname):
        os.mkdir(path=projname)
        os.chmod(path=projname, mode=0o2774)
        # return render_template('index.html', tree=make_tree(path), file_contents="IEEE;") 
    else:
        flash('The project already exists', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg) 


# https://gist.github.com/andik/e86a7007c2af97e50fbb
@app.route('/')
@htpasswd.required
def index(user):
    print(f"{user} has successfully logged in")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg)


@app.route('/get_file', methods=["GET"])
@htpasswd.required
def get_file(user):
    file_contents = open(request.args.get('filename').strip(), 'r').read()
    data = {
            "contents" : file_contents,
        }
    return jsonify(data)


@app.route('/save_file', methods=["POST", "GET"])
@htpasswd.required
def save_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    if request.method == 'POST':
        body = request.json

        # Write the data to the file
        with open(body["current_file"], "w") as file:
            file.write(body["file_contents"])
    
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg)


if __name__=="__main__":
    app.run(host='localhost', port=8080, debug=True, use_reloader=True)