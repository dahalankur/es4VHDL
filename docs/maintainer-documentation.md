
## Project Structure
This explains how the project is structured, and how it is intended to be used. This section is not intended to be a user guide for the project.

### Web Application Setup
There are some steps to be taken in the beginning of the semester to set up the web application. These steps are explained in this section. Firstly, the repository where the web application resides is es4VHDL. Once you have this repository cloned in a directory on the Halligan servers, there are some steps you need to take in order to ensure every file that we need is present. Go to the bin/ directory and delete fpga-toolchain, as we will need a fresh version of the toolchain with all the binaries present. Go to this website to get the latest version of the toolchain: https://github.com/YosysHQ/fpga-toolchain/releases/tag/nightly-20211006. Copy the link for the nightly version of linux, and download it to es4vhdl/bin.
![fpga toolchain binary on Github releases](images/fpga-toolchain.png)

You can use the wget tool to download this from the command line. For example:
![Nightly FPGA Toolchain downloaded](images/fpga-toolchain-linux.png)
> vm-hw00{adahal01}139: wget "https://github.com/YosysHQ/fpga-toolchain/releases/download/nightly-20211006/fpga-toolchain-linux_x86_64-nightly-20211006.tar.xz"

Once the download is complete, the bin/ directory should look like this:
![directory after downloading](images/bin-after-download.png)

Now, we have to extract the toolchain. To do so, we can use tar:
> vm-hw00{adahal01}175: tar -xf fpga-toolchain-linux_x86_64-nightly-20211006.tar.xz

Wait for the directory to be extracted, and after it’s done, we can delete the tar.xz file. The bin/ directory should now look like this:


Great! This is all the set up we need to do for the web application.

### Student Account Setup (Groups and Passwords)
Students that are enrolled in the class must be a member of the es4vhdl unix group on the Halligan servers. Please contact Michael Bauer to add all the enrolled students to this group. Furthermore, all students must run a one-time script to set up all the necessary directories and permissions in the home directory on the Halligan servers. This is the setup.sh script which is present in the bin/ directory of  the repository. This sets up the directory for the web application per user, fixes permissions and imports a sample project.

Like in VHDLWeb, you need to generate passwords for each enrolled student in the class. The password hashes for each student is stored in a .htpasswd file in the root directory of the repository. For obvious security reasons, this file is not version controlled and it must only have rw permissions for the user (i.e., chmod 600 .htpasswd). The script to add passwords to this .htpasswd file is called add_user, and is located in the root directory of the repository.
- In the beginning of the semester, generate random passwords for each user enrolled in the class. It must be noted that the username must be their UTLN. To add the password hash to the aforementioned .htpasswd file, use the add_user script, supplying the username as the first command line argument. An example of adding a password for the user “test123” is shown below:
    - ![Add User](images/add_user.png)
    - If you inspect the htpasswd file now, you should see an entry for the user “test123” like this: test123:$apr1$5cy/Fl4o$sRZgwg9pXhIqv29gd4d1t/
    - Repeat this for all students enrolled in the class
Once this is done, you can send the students their credentials and instructions to run the setup.sh script once (but only after you have read the section on setting up a sample project). Once that is done, they should be able to use the website once the server is up and running!

### How to run the server + view logs
To run the server, go to the root directory where the repository is located and simply execute the run_server script. All logs are automatically piped to the err.log file in the same directory. The logs are prepended by the username of the student, the timestamp, and the log level (INFO, ERROR, or WARNING). The web app runs using gunicorn on port 8080 by default, but this can be changed in the run_server script.

### How to view snapshots
On every build, a “snapshot” of the student’s current project is taken by the web application and copied to a hidden directory in the root directory of the repository. This directory is called .backup/. It stores timestamped project directories for all students. An example structure of a .backup directory is shown below:
![backups](images/backups.png)


Individual student project backups look like this:
![individual backups](images/individual-backups.png)

## Sample Project Documentation 
where this folder should sit
- After running the setup.sh script, each student will have a sample project that will go through the files needed to get started with the web application (config, pin constraints, etc.). If you inspect the setup.sh script, there is a variable with a path to this sample project:
![Setup script image](images/setup-script.png)

- When you cloned the repository, the sample project should also be present in the starterproject/adder directory. Please move the adder directory to your public_html directory on the Halligan servers, with permissions as shown below:
![Public HTML ls](images/public_html.png)


- Once this is done, go to setup.sh and change the server_project_dir to point to the adder directory in your public_html folder. That should do it for setting up the sample project! Finally, the setup.sh script can be run by the students to set up their environment.


### Dependencies
This project is intended to be hosted on the Tufts University Electrical Engineering and Computer Science Department's servers. As such, it is currently run in production using following setup
- Backend enviornment: Red Hat Enterprise Linux
- Every user is expected to have a user account on the server
    - accounts are in the form `/h/USERNAME`
        - `/h/ebrown26` for example, where ebrown26 is the student UTLN.
- Every user has run the [installation script](bin/setup.sh) before using the web IDE

## Installation
This section is intended to be used by the Tufts University EECS admins, not by students. For students, please see [Usage](#Usage)

- Clone the repository
- Install the needed FPGA toolchains [TODO](#TODO)


### System Design
![SystemArchitecture](SystemArchitecture.png)
#### File Layout
- Frontend: HTML/CSS and Javascript. Found in [templates/index.html](templates/index.html) and [templates/layout.html](templates/layout.html).
- Backend: Flask server, found in [app.py](app.py)
    - Server is started by running `./run_server`, which can be found in [run_server](run_server). Make sure to make this script executable by first typing `chmod +x run_server`
- Database: None. The backend is the Tufts University EECS servers, which are used to store the user's files. If you were running this project outside of that enviornment, it is recommended you use a blobstore to store the user's files. See [Dependencies](#Dependencies) for more information on the EECS servers.

#### Request Handling
The frontend does `fetch()` requests to the backend for all resources, to save files, and open files. The backend processes these files directly on the file system, then serves them to the frontend. The frontend then renders the files as needed.

