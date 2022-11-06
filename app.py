import os
import shutil
from build_files import safe_run
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_htpasswd import HtPasswdAuth

# TODO: vulnerability: if the user sends some other path in one of the GET requests, we will currently run the command for another user. We do not want this, so we want 
# to check that the path being provided is a subdirectory of the user's home directory.

default_msg = '''
Welcome to ES4 VHDL online editor!

Begin by creating a new project, or selecting an existing one!
'''
# TODO: add a link to help/documentation page in default_msg

# TODO: create a separate config file for all flask configs
app = Flask(__name__)
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['SECRET_KEY'] = os.urandom(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

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
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200


@app.route('/delete_folder', methods = ['GET'])
@htpasswd.required
def delete_folder(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_delete = request.args.get('current_dir')
    if os.path.exists(path=to_delete):
        if not os.path.isdir(to_delete):
            flash('Cannot delete non-directory', 'error')
            return redirect(url_for('index'))
        # Delete the file
        shutil.rmtree(to_delete, ignore_errors=False, onerror=None)
    else:
        flash('No directory with the given name exists', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200


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
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200
 

@app.route('/new_project', methods = ['GET'])
@htpasswd.required
def new_project(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    projname = path + request.args.get('projname')

    if not os.path.exists(path=projname):
        os.mkdir(path=projname)
        os.chmod(path=projname, mode=0o2775)
    else:
        flash('The project already exists', 'error')
        return redirect(url_for('index'))
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200

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
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200



# https://gist.github.com/andik/e86a7007c2af97e50fbb
@app.route('/')
@htpasswd.required
def index(user):
    print(f"{user} has successfully logged in")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg)

# TODO: make a 'log' function instead of print that writes to a log file

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
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200


'''
In analysis mode, GHDL compiles one or more files, and creates an object file for each source file. The analysis mode is selected with -a switch. Any argument starting with a dash is a option, the others are filenames. No option is allowed after a filename argument. GHDL analyzes each filename in the given order, and stops the analysis in case of error (the following files are not analyzed).
'''
@app.route('/analyze_ghdl_file', methods=['GET'])
@htpasswd.required
def analyze_ghdl_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_analyze = request.args.get('filename')
    if not os.path.exists(path=to_analyze):
        flash("No such file exists")
        return redirect(url_for('index'))

    # remove work-obj08.cf if it exists
    if os.path.exists(path=os.path.join(os.path.dirname(to_analyze), "work-obj08.cf")):
        os.remove(path=os.path.join(os.path.dirname(to_analyze), "work-obj08.cf"))
    
    # build with ghdl in their directory (to prevent race conditions when multiple users are compiling)
    output = safe_run(["ghdl", "-a", "-fsynopsys", "--std=08", to_analyze], cwd=os.path.dirname(to_analyze),timeout=5).decode("utf-8")
    build_success = os.path.exists(path=os.path.join(os.path.dirname(to_analyze), "work-obj08.cf"))

    data = {
            "output" : output,
            "success" : build_success
        }
    
    return jsonify(data)

if __name__=="__main__":
    app.run(host='localhost', port=8080, debug=True, use_reloader=True)