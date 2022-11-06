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
    tree = dict(name=os.path.basename(path), children=[], path="", dirname=path)
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                # This is not a directory
                tree['children'].append(dict(name=name, path=fn))
    return tree

# TODO: Update the size of the file tree and the editor window to be correct.

@app.route('/delete_file', methods = ['GET'])
@htpasswd.required
def delete_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_delete = request.args.get('filename')
    if os.path.exists(path=to_delete):
        if not os.path.isfile(path=to_delete):
            flash('Cannot delete non-file', 'error')
            return redirect(url_for('index'))
        # Delete the file
        os.remove(to_delete)
    else:
        flash('No file with the given name exists', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg) 


@app.route('/new_folder', methods = ['GET'])
@htpasswd.required
def new_folder(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    current_dir = request.args.get('current_dir')
    new_dir = current_dir + "/" + request.args.get('dirname')
    
    if os.path.exists(path=current_dir):
        if os.path.exists(path=new_dir):
            flash('The directory with the given name already exists', 'error')
            return redirect(url_for('index'))
        
        # Create the new directory with appropriate permissions
        os.mkdir(path=new_dir)
        os.chmod(path=new_dir, mode=0o2775)
    else:
        flash('The path to the current directory does not exist', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg) 
 

@app.route('/new_project', methods = ['GET'])
@htpasswd.required
def new_project(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    projname = path + request.args.get('projname')
    print(projname)
    if not os.path.exists(path=projname):
        os.mkdir(path=projname)
        os.chmod(path=projname, mode=0o2775)
    else:
        flash('The project already exists', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg) 

@app.route('/new_file', methods = ['GET'])
@htpasswd.required
def new_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    current_dir = request.args.get('current_dir')
    filename = current_dir + "/" + request.args.get('filename')

    if os.path.exists(path=current_dir):
        if os.path.exists(path=filename):
            flash('The file with the given name already exists', 'error')
            return redirect(url_for('index'))
        
        open(filename, "w")
        os.chmod(path=filename, mode=0o660)
    else:
        flash('The specified folder does not exists', 'error')
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