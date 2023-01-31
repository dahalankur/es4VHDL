import os
import shutil
import json
import requests
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
        # Make a new file "config.json"
        config_file = projname + "/" + "config.json"
        with open(config_file, "w") as f:
            f.write('{\n\t"project": "' + request.args.get('projname') + '",\n \t"toplevel": "",\n\t"testbench": "",\n\t"src": [],\n\t"pins": { }\n}')
        os.chmod(path=config_file, mode=0o660)
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

# TODO: make a 'log' function instead of print that writes to a log file or figure out where gunicorn logs are written to

@app.route('/get_file', methods=["GET"])
@htpasswd.required
def get_file(user):
    file_contents = open(request.args.get('filename').strip(), 'r').read()
    data = {
            "contents" : file_contents,
        }
    return jsonify(data)

#TODO: use sbell's netlist template

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

def perform_synthesis(to_synthesize):
    if not os.path.exists(path=to_synthesize):
        flash("No such file exists")
        return redirect(url_for('index'))

    # remove work-obj08.cf if it exists
    if os.path.exists(path=os.path.join(os.path.dirname(to_synthesize), "work-obj08.cf")):
        os.remove(path=os.path.join(os.path.dirname(to_synthesize), "work-obj08.cf"))
    
    # remove an svg file if it exists
    if os.path.exists(path=os.path.join(os.path.dirname(to_synthesize), f"{to_synthesize}-netlist.svg")):
        os.remove(path=os.path.join(os.path.dirname(to_synthesize), f"{to_synthesize}-netlist.svg"))
        

    # call synthesize.sh script with the filename as an argument
    # get python script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # set GHDL_PREFIX env variable 
    os.environ["GHDL_PREFIX"] = f"{script_dir}/bin/fpga-toolchain/lib/ghdl/"
    output = safe_run([f"{script_dir}/bin/synthesize.sh", to_synthesize], cwd=os.path.dirname(to_synthesize),timeout=5).decode("utf-8")
    build_success = os.path.exists(path=os.path.join(os.path.dirname(to_synthesize), f"{to_synthesize}-netlist.svg"))
    
    data = {
        "output" : output,
        "success" : build_success
    }

    return jsonify(data)


@app.route('/synthesize_file', methods=['GET'])
@htpasswd.required
def synthesize_file(user):
    return perform_synthesis(request.args.get('filename'))


@app.route("/build", methods=['GET'])
@htpasswd.required
def build(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    directory = request.args.get('directory')
    makefile_path = f'{directory}/Makefile'

    # generate Makefile based on config.json
    makefile = generate_makefile(f'{directory}/config.json')
    with open(makefile_path, "w") as f: f.write(makefile)
    
    # generate pin constraints file based on config.json
    pin_constraints = generate_pinconstraint(f'{directory}/config.json')
    
    with open(f'{directory}/pin_constraints.pdc', "w") as f: f.write(pin_constraints)
    

    output = safe_run(['make', '-j', f'--directory={directory}'], cwd=os.path.dirname(directory) + "/" + os.path.basename(directory), timeout=5).decode("utf-8")
    

    print(output)
    
    success = False
    if "Build successful" in output:
        success = True
    
    # TODO: return success status to the frontend somehow

    # print("Build status: ", success)
    
    os.chmod(path=makefile_path, mode=0o660)
    
    # from config.json, get the toplevel module
    toplevel = ""
    with open(f'{directory}/config.json', 'r') as f:
        config = json.load(f)
        toplevel = config['toplevel'] if config['toplevel'].endswith('.vhd') else config['toplevel'] + '.vhd'

    # after build is complete, synthesize the top module
    if success and toplevel != "":
        out = perform_synthesis(directory + "/" + toplevel)

        # json to dict and check for success 
        out = json.loads(out.data)
        # TODO: check success status later

        # fix permissions
        for file in os.listdir(directory): 
            # directory
            if os.path.isdir(os.path.join(directory, file)):
                os.chmod(path=os.path.join(directory, file), mode=0o2775)
            else:
                os.chmod(path=os.path.join(directory, file), mode=0o660)

        # TODO: show build output in the box! return it as a response
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200

def generate_pinconstraint(config):
    # check if config file exists
    if not os.path.exists(path=config):
        flash("config.json does not exist")
        return redirect(url_for('index'))
    else:
        # read from config.json the pin mappings
        with open(config, "r") as f:
            config = json.load(f)
            pins = config["pins"]
            pins_str = ""
            for varName, pinNumber in pins.items():
                pins_str += f"ldc_set_location -site {{{pinNumber}}} [get_ports {varName}]\n"



            return pins_str

def generate_makefile(config):
    # check if config file exists
    if not os.path.exists(path=config):
        flash("config.json does not exist")
        return redirect(url_for('index'))
    else:
        # read from config.json the files to compile
        with open(config, "r") as f:
            config = json.load(f)
            toplevel_src = config["toplevel"] if config["toplevel"].endswith(".vhd") else config["toplevel"] + ".vhd"
            src_files = " ".join(config["src"]) + " " + toplevel_src
            if config["toplevel"].endswith(".vhd"):
                entity = config["toplevel"][0 : config["toplevel"].index(".vhd")]
            else:
                entity = config["toplevel"]
    
        return f"""
##########################################
#                                        #
#       Auto generated Makefile          #
#             DO NOT EDIT                #
#                                        #
##########################################
GHDL = ghdl
FILES = {src_files}
ENTITY = {entity}
FLAGS = --std=08

all:
\t@$(GHDL) -a $(FLAGS) $(FILES)
\t@$(GHDL) -e $(FLAGS) $(ENTITY)
\t@$(GHDL) -r $(FLAGS) $(ENTITY) --wave=wave-top.ghw
\t@rm -rf wave-top.ghw work-obj08.cf
\t@echo 'Build successful'
"""

# TODO: use safe_run for synthesis
    

if __name__=="__main__":
    app.run(host='localhost', port=8080, debug=True, use_reloader=True)




'''
Example .toml file (backup for config.json)

[projectConfig]
project  = "project name"
toplevel = "sevenseg.vhd"
testbench = "none"
src = ["seveseg.vhd", "alu.vhd"]

[pins]
clk = 1
A_0 = 2
A_1 = 2
B_2 = 3

'''
