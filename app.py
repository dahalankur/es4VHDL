import os
import shutil
import tempfile
from datetime import datetime
import json
import toml
import logging
from pathlib import Path
from build_files import safe_run
from flask import Flask, render_template, request, flash, redirect, send_from_directory, url_for, jsonify, send_file
from flask_htpasswd import HtPasswdAuth

# TODO: vulnerability: if the user sends some other path in one of the GET requests, we will currently run the command for another user. We do not want this, so we want 
# to check that the path being provided is a subdirectory of the user's home directory.

#  --------- LOGGING INFO -----------

# @app.route('/')
# def default_route():
#     """Default route"""
#     app.logger.debug('this is a DEBUG message')
#     app.logger.info('this is an INFO message')
#     app.logger.warning('this is a WARNING message')
#     app.logger.error('this is an ERROR message')
#     app.logger.critical('this is a CRITICAL message')

#  ------ END OF LOGGING INFO ---------



# ----------- JSON RESPONSE INFO -------------
# Every response from the server should be a
# JSON object for normal responses
#
# { 'result'  : 'success' | 'fail',
#   'message' : 'some message',
#   'tree'   ?: tree_data }
# ---------- END OF JSON RESPONSE INFO -------


default_msg = '''
Welcome to ES4 VHDL online editor!

Begin by creating a new project, or selecting an existing one!

'''
# TODO: add a link to help/documentation page in default_msg

# TODO: create a separate config file for all flask configs
app = Flask(__name__)
# TODO: change this later; use a config file to store all flask config secrets
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['FLASK_HTPASSWD_PATH'] = '.htpasswd'
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.jinja_env.auto_reload = True

# Set up Flask to log errors to a file (in addition to the console by default)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.setLevel(gunicorn_logger.level)
app.logger.handlers = gunicorn_logger.handlers


htpasswd = HtPasswdAuth(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# TODO: change this, simplify the workflow later when dealing with frontend
# TODO: Update the size of the file tree and the editor window to be correct.
def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[], path="", dirname=path)
    try: lst = os.listdir(path)
    except OSError:
        pass # ignore errors TODO: not the very best practice is it? :)
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                # This is not a directory
                tree['children'].append(dict(name=name, path=fn))
    return tree

# TODO: Eventually remove this route, as every other route should
# return the tree, and the tree should be updated on the frontend
# This therefore does not to be called ever.
@app.route('/get_tree', methods = ['GET'])
@htpasswd.required
def get_tree(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return jsonify(make_tree(path))

@app.route('/delete_file', methods = ['GET'])
@htpasswd.required
def delete_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_delete = request.args.get('filename')
    if os.path.exists(path=to_delete):
        if not os.path.isfile(path=to_delete):
            err_msg = f"{user}: Cannot delete non-file {to_delete}"
            app.logger.error(err_msg)
            return jsonify({ "tree": make_tree(path), 
                            "result": 'fail',
                             "message": err_msg })
        # Delete the file
        try:
            os.remove(to_delete)
            app.logger.info(f"{user}: Deleted file {to_delete}")
        except Exception as error:
            app.logger.error(f"{user}: Error deleting file {to_delete} -> ", error)
            # TODO: send to frontend
    else:
        # TODO: send message to frontend about file not existing
        app.logger.error(f"{user}: File {to_delete} does not exist")
        return jsonify({ "tree": make_tree(path), 
                         "result": 'fail', 
                         "message": f'File {to_delete} does not exist'})
    return jsonify({ "tree": make_tree(path), "result": 'success', "message": '' })


@app.route('/delete_folder', methods = ['GET'])
@htpasswd.required
def delete_folder(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_delete = request.args.get('current_dir')
    if os.path.exists(path=to_delete):
        if not os.path.isdir(to_delete):
            err_msg = f"{user}: Cannot delete non-folder {to_delete}"
            app.logger.error(err_msg);
            # TODO: send message to frontend about folder not being able to be deleted
            return jsonify({ "tree": make_tree(path),
                             "result": 'fail', 
                             "message": err_msg })
        # Delete the folder
        try:
            shutil.rmtree(to_delete, ignore_errors=False, onerror=None)
            app.logger.info(f"{user}: Deleted folder {to_delete}")
        except Exception as error:
            app.logger.error(f"{user}: Error deleting folder {to_delete} -> ", error)
            # TODO: send to frontend
    else:
        # TODO: send message to frontend about folder not existing
        app.logger.error(f"{user}: Folder {to_delete} does not exist")
        return jsonify({ "tree": make_tree(path), "result": 'fail', "message": f'Folder {to_delete} does not exist' })
    return jsonify({ "tree": make_tree(path), "result": 'success', "message": '' })


@app.route('/new_folder', methods = ['GET'])
@htpasswd.required
def new_folder(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    current_dir = request.args.get('current_dir')
    new_dir = current_dir + "/" + request.args.get('dirname')
    
    if os.path.exists(path=current_dir):
        if os.path.exists(path=new_dir):
            # TODO: send message to frontend about directory already existing
            err_msg = f"{user}: Directory {new_dir} already exists"
            app.logger.error(err_msg)
            return jsonify({ "tree": make_tree(path), 
                            "result": 'fail', 
                            "message": err_msg })
    
        try:
        # Create the new directory with appropriate permissions
            os.mkdir(path=new_dir)
            os.chmod(path=new_dir, mode=0o2775)
            app.logger.info(f"{user}: Created directory {new_dir}")
        except Exception as error:
            app.logger.error(f"{user}: Error creating directory and/or changing permissions -> ", error)
            # TODO: send to frontend
    else:
        # TODO: send message to frontend about file not being able to be created
        err_msg = f"{user}: Path to directory {new_dir} does not exist"
        app.logger.error(err_msg)
        return jsonify({ "tree": make_tree(path), 
                         "result": 'fail', 
                         "message": err_msg })
 

@app.route('/new_project', methods = ['GET'])
@htpasswd.required
def new_project(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    projname = path + request.args.get('projname')

    if not os.path.exists(path=projname):
        try:
            os.mkdir(path=projname)
            os.chmod(path=projname, mode=0o2775)
            
            # Make a new file "config.toml"
            config_file = projname + "/" + "config.toml"
            with open(config_file, "w") as f:
                config_contents = f"""project = "{request.args.get('projname')}"
toplevel  = ""   # Place your toplevel entity here
testbench = ""   # (Optional) Place the name of your test bench here
src       = []   # List all vhd files you need to build your project 

# List your variable to FPGA pin-mappings here
[pins]
# "var1" = 1
# "var2" = 32
# "clk"  = 8
"""
                f.write(config_contents)
            os.chmod(path=config_file, mode=0o660)
            app.logger.info(f"{user}: Created project {projname}")
        except Exception as error:
            app.logger.error(f"{user}: Error creating project and/or changing permissions -> ", error)
            # TODO: send this to frontend
    else:
        app.logger.error(f"{user}: Project {projname} already exists")
        # TODO: send this to frontend
    return jsonify({ "tree": make_tree(path), 
                    "result": 'success', 
                    "message": '' })

@app.route('/new_file', methods = ['POST'])
@htpasswd.required
def new_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    body = request.json
    current_dir= body['current_dir']
    filename = current_dir + "/" + body['filename']

    response = {"contents" : "", "success" : False}
    
    if os.path.exists(path=current_dir):
        if os.path.exists(path=filename):
            error_msg = f"File {filename} already exists"
            app.logger.error(f"{user}: {error_msg}")
            # TODO: send to frontend
            return jsonify({"contents" : error_msg, 
                            "result": 'fail',
                              "message": error_msg})
        try:
            open(filename, "w")
            os.chmod(path=filename, mode=0o660)
            app.logger.info(f"{user}: Created file {filename}")
        except Exception as error:
            err_msg = f"{user}: Error creating file and/or changing permissions -> ", error
            app.logger.error(err_msg)
            return jsonify ({ "contents" : err_msg, 
                             "result": 'fail',
                               "message": err_msg})
    else:
        err_msg = f"{user}: Directory {current_dir} does not exist"
        app.logger.error(err_msg)
        return jsonify({'result': 'fail', 
                        'message': err_msg,
                        "tree":make_tree(path)})
    
    return jsonify({'result': 'success',
                    'message': 'Successfully created the new file',
                    "tree": make_tree(path)})

    
    # return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200



# https://gist.github.com/andik/e86a7007c2af97e50fbb
@app.route('/')
@htpasswd.required
def index(user):
    app.logger.info(f"{user}: Logged in")
    path = os.path.expanduser(f'/h/{user}/.es4/')
    return render_template('index.html', tree=make_tree(path), file_contents=default_msg)


@app.route('/get_file', methods=["GET"])
@htpasswd.required
def get_file(user):
    data = {"contents" : ""}
    try:
        filename = request.args.get('filename').strip()
        file_contents = open(filename, 'r').read()
        data = {
                "contents" : file_contents,
            }
        app.logger.info(f"{user}: Opened {filename}")
    except Exception as error:
        app.logger.error(f"{user}: Error opening file {filename} -> ", error)
        # TODO: send to frontend
    return jsonify(data)

@app.route('/get_binary_file', methods=["GET"])
@htpasswd.required
def get_binary_file(user):
    data = {"contents" : ""}
    try:
        filename = request.args.get('filename').strip()
        app.logger.info(f"{user}: Opened {filename}")
        return send_file(filename, as_attachment=True)
    except Exception as error:
        app.logger.error(f"{user}: Error opening file {filename} -> ", error)
        # TODO: send to frontend
    # get only the file name
    return jsonify({"content": ""})

@app.route('/get_zipped_folder', methods=["GET"])
@htpasswd.required
def get_zipped_folder(user):
    data = {"contents" : ""}
    try:
        to_zip = request.args.get('directory')
        app.logger.info(f"{user}: Opened {to_zip}")
        tempdir = tempfile.mkdtemp()
        proj_tempdir = tempdir + '/' + os.path.basename(to_zip)
        shutil.copytree(to_zip, proj_tempdir)
        output_filename = proj_tempdir + '.zip'
        shutil.make_archive(proj_tempdir, 'zip', proj_tempdir)
        return send_file(output_filename, as_attachment=True)
    except Exception as error:
        app.logger.error(f"{user}: Error opening file {to_zip} -> ", error)
    return jsonify({"content": ""})
    

@app.route('/save_file', methods=["POST"])
@htpasswd.required
def save_file(user):
    print('User in save file', user)
    path = os.path.expanduser(f'/h/{user}/.es4/')
    body = request.json
    print(body)
    filename = body["current_file"]
    # Write the data to the file
    try:
        with open(filename, "w") as file:
            file.write(body["file_contents"])
        app.logger.info(f"{user}: Saved data to {filename}")
    except Exception as error:
        app.logger.error(f"{user}: Error saving file {filename} -> ", error)
        # TODO: send to frontend
    return jsonify({"contents": "Saved file", "success" : True})
#    return render_template('index.html', tree=make_tree(path), file_contents=default_msg), 200


'''
In analysis mode, GHDL compiles one or more files, and creates an object file for each source file. The analysis mode is selected with -a switch. Any argument starting with a dash is a option, the others are filenames. No option is allowed after a filename argument. GHDL analyzes each filename in the given order, and stops the analysis in case of error (the following files are not analyzed).
'''
@app.route('/analyze_ghdl_file', methods=['GET'])
@htpasswd.required
def analyze_ghdl_file(user):
    path = os.path.expanduser(f'/h/{user}/.es4/')
    to_analyze = request.args.get('filename')
    if not os.path.exists(path=to_analyze):
        app.logger.error(f"{user}: File {to_analyze} does not exist")
        # TODO: send to frontend
        return redirect(url_for('index'))

    data = {"output" : "", "success" : False}
    
    try:
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
        app.logger.info(f"{user}: Ran analysis on file {to_analyze}")
    except Exception as error:
        app.logger.error(f"{user}: Error analyzing file {to_analyze} -> ", error)
        # TODO: send to frontend
    
    return jsonify(data)


def perform_synthesis(user, to_synthesize):
    # TODO: use sbell's netlist template (add stuff to static later, look at his vhdlweb repo for details)
    if not os.path.exists(path=to_synthesize):
        app.logger.error(f"{user}: File {to_synthesize} does not exist")
        # TODO: send to frontend
        return redirect(url_for('index'))

    data = {"output" : "", "success" : False}

    try:
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
        synthesized_netlist = Path(to_synthesize).stem  +  "-netlist.svg"
        build_success = os.path.exists(path=os.path.join(os.path.dirname(to_synthesize), synthesized_netlist))

        data = {
            "output" : output,
            "success" : build_success
        }
        app.logger.info(f"{user}: Ran synthesis script on file {to_synthesize}")
    except Exception as error:
        app.logger.error(f"{user}: Error synthesizing file {to_synthesize} -> ", error)
        # TODO: send to frontend
    return jsonify(data)


@app.route('/synthesize_file', methods=['GET'])
@htpasswd.required
def synthesize_file(user):
    return perform_synthesis(user, request.args.get('filename')) # TODO: evaluate the "success" status in the frontend

@app.route("/generate_bin", methods=['POST', 'GET'])
@htpasswd.required
def generate_bin(user):
    # build(user) TODO: assume project has already been built (FOR TESTING ONLY)
    # from config.toml, get the toplevel module
    toplevel = ""
    try:
        path = os.path.expanduser(f'/h/{user}/.es4/')
        # directory = request.args.get('directory') get this from the post request
        directory = request.json['directory']
        with open(f'{directory}/config.toml', 'r') as f:
            config = toml.load(f)
            toplevel = config['toplevel'] if config['toplevel'].endswith('.vhd') else config['toplevel'] + '.vhd'
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output = safe_run([f"{script_dir}/bin/generate_bin.sh", f'{directory}/{toplevel}'], cwd=os.path.dirname(directory),timeout=30).decode("utf-8")
        # print(script_dir, output, toplevel, directory) # TODO: log here
        bitstream = Path(toplevel).stem  +  ".bin"
        build_success = "Info: Program finished normally." in output
        app.logger.info(f"{user}: Generated bitstream for project {directory}")
        print('success sent')
        return jsonify({
            "output" : output,
            "success" : build_success,
            "tree": make_tree(path)
        })
    except Exception as error:
        message = f'Error generating bin file for toplevel entity {toplevel}'
        app.logger.error(f"{user}: {message} -> ", error)
        return jsonify({
            "output" : output,
            "success" : False,
            "tree": '',
            "message": message,
        })

    
  

   

@app.route("/build", methods=['POST'])
@htpasswd.required
def build(user):
    print('User in build: ', user)
    path = os.path.expanduser(f'/h/{user}/.es4/')
    directory = request.json['directory']
    makefile_path = f'{directory}/Makefile'
    
    # generate Makefile based on config.toml
    makefile = generate_makefile(user, f'{directory}/config.toml')
    if makefile == "":
        app.logger.error(f"{user}: Error getting makefile contents from config.toml")
        return jsonify({
            "output" : '',
            "success" : False,
            "tree": '',
            "message": "Error getting makefile contents from config.toml",
        })
    
    try:
        with open(makefile_path, "w") as f: f.write(makefile)
    except Exception as error:
        message = f'Error writing Makefile contents to {makefile_path}'
        app.logger.error(f"{user}: Error writing Makefile contents to {makefile_path} -> ", error)
        return jsonify({
            "output" : output,
            "success" : False,
            "tree": '',
            "message": message,
        })
        
    # generate pin constraints file based on config.toml
    pin_constraints = generate_pinconstraint(user, f'{directory}/config.toml')
    if pin_constraints == "":
        app.logger.warning(f"{user}: Error getting pin constraints from config.toml")

    output = ""

    try:
        with open(f'{directory}/pin_constraints.pcf', "w") as f: f.write(pin_constraints)
        
        output = safe_run(['make', '-j', f'--directory={directory}'], cwd=os.path.dirname(directory) + "/" + os.path.basename(directory), timeout=5).decode("utf-8")

        success = False
        if "Build successful" in output:
            success = True

        os.chmod(path=makefile_path, mode=0o660)
        app.logger.info(f"{user}: Ran make on project {directory}")

        # -------- back up begins here --------
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # create a user-specific backup directory if it doesn't exist
        backup_dir = f'{script_dir}/.backup/{user}'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            os.chmod(backup_dir, mode=0o2770)
            shutil.chown(backup_dir, user=None, group='es4vhdl-admin')
        
        # create a project-specific backup directory if it doesn't exist
        project_backup_dir = f'{backup_dir}/{os.path.basename(directory)}'
        if not os.path.exists(project_backup_dir):
            os.makedirs(project_backup_dir)
            os.chmod(project_backup_dir, mode=0o2770)
            shutil.chown(backup_dir, user=None, group='es4vhdl-admin')

        curr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        shutil.copytree(directory, f'{project_backup_dir}/{curr_time}')

        # -------- back up ends here --------

    except Exception as error:
        message = f'Error building project {directory}'
        app.logger.error(f"{user}: {message}")
        return jsonify({'result': 'error',
                        'tree': '',
                        'output': output,
                        'message': message
        })
    # from config.toml, get the toplevel module
    toplevel = ""
    try:
        with open(f'{directory}/config.toml', 'r') as f:
            config = toml.load(f)
            toplevel = config['toplevel'] if config['toplevel'].endswith('.vhd') else config['toplevel'] + '.vhd'

        # after build is complete, synthesize the top module
        if success and toplevel != "":
            out = json.loads(perform_synthesis(user, directory + "/" + toplevel).data)
            if (not out['success']):
                message = f'Cannot synthesize netlist for project {directory}'
                app.logger.error(f"{user}: {message}")
                return jsonify({'result': 'error',
                                'tree': '',
                                'output': output,
                                'message': message
                })
            

        else:
            message = f"Error performing synthesis on top module {toplevel}"
            app.logger.error(f"{user}: {message}")
            
            return jsonify({'result': 'error',
                            'tree': '',
                            'output': output,
                            'message': message
            })
        # fix permissions
        for file in os.listdir(directory): 
            # directory
            if os.path.isdir(os.path.join(directory, file)):
                os.chmod(path=os.path.join(directory, file), mode=0o2775)
            else:
                os.chmod(path=os.path.join(directory, file), mode=0o660)
    except Exception as error:
        message = f"Error performing synthesis on top module {toplevel} and/or changing permissions"
        app.logger.error(f"{user}: {message} -> ", error)
        return jsonify({'result': 'error',
                        'tree': '',
                        'output': output,
                        'message': message
        })

    app.logger.info(f"{user}: Ran build script on {directory}")
    return jsonify({'result': 'success',
                    'tree': make_tree(path),
                    'output': output,
                    'message': ''    
    })

def generate_pinconstraint(user, config):
    if not os.path.exists(path=config):
        app.logger.error(f"{user}: File {config} does not exist")
        # TODO: send to frontend
        return ""
    else:
        # read the pin mappings from config.toml
        pins_str = ""
        try:
            with open(config, "r") as f:
                config = toml.load(f)
            pins = config["pins"]
            for varName, pinNumber in pins.items():
                pins_str += f"set_io {varName} {pinNumber}\n"
            app.logger.info(f"{user}: Generated pin constraints from config: {config}")
        except Exception as error:
            # TODO: send to frontend
            app.logger.error(f"{user}: Error generating pin constraints from config: {config} -> ", error)
            return ""
        return pins_str

def generate_makefile(user, config):
    # check if config file exists
    if not os.path.exists(path=config):
        app.logger.error(f"{user}: File {config} does not exist")
        return ""
    else:
        # read from config.toml the files to compile
        try: 
            with open(config, "r") as f:
                config = toml.load(f)
                toplevel_src = config["toplevel"] if config["toplevel"].endswith(".vhd") else config["toplevel"] + ".vhd"
                src_files = " ".join(config["src"]) + " " + toplevel_src
                if config["toplevel"].endswith(".vhd"):
                    entity = config["toplevel"][0 : config["toplevel"].index(".vhd")]
                else:
                    entity = config["toplevel"]
            app.logger.info(f"{user}: Generated makefile string from config: {config}")
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
        except Exception as error:
            app.logger.error(f"{user}: Error generating Makefile from config: {config} -> ", error)
            # TODO: send to backend
            return ""

# TODO: use safe_run for synthesis and build and other external calls

# Serves the image for edit icon
@app.route('/images/edit-icon.png', methods=['GET'])
def get_edit_icon():
    # the image is in static/edit_icon.jpeg
    return send_from_directory('static', 'edit-icon.png')

if __name__=="__main__":
    app.run(host='localhost', port=8080, debug=True, use_reloader=True)
