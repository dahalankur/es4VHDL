## Platform Agnostic Web IDE for ICE40 FPGAs
> Capstone Project, Tufts Universtiy, 2023
> Sponsor: Professor Steven Bell of the EECS department at Tufts University

## Project Description
This project builds a platform-agnostic web ide for ICE40 FPGAs. Users will be able to [build projects](#TODO), [Compile their code to bitstreams](#TODO), and [flash their bitstreams to their FPGA](#TODO) all from the comfort of their web browser and a GUI application. This project is built using [Flask](https://flask.palletsprojects.com/en/2.0.x/) for the backend, and vanilla html and javascript for the frontend.

This is intended to be used in combination with ES4 and other related courses which use VHDL and ice40 FPGAs


## Usage
This section is intended to explain how a project would be used, from the perspective of a student in ES4. This section is not intended to be a technical overview of the project, but rather a user guide for the project.

> Requirement: The first time you use the project, make sure to run the installation script on your EECS account (ssh <utln>@homework.cs.tufts.edu). Please run the following command in your home directory on terminal: `wget https://raw.githubusercontent.com/dahalankur/es4VHDL/main/bin/setup.sh && chmod +x setup.sh && ./setup.sh`

1. Make sure you have been added to the es4vhdl group on the file system. Contact your professor or [staff@eecs.tufts.edu](mailto:staff@eecs.tufts.edu) for help with this.
2. Log into the website using your UTLN and __special password provided by the professor__. This is NOT your typical EECS password. If you do not have this password, please contact your professor.
3. Create a new project button. Use the toggle button "Create Buttons" to show you these options. You can create a new project, or import an existing project from your file system. To import an existing project, ask help from your professor.
4. Once you have created a project, you can click on the project name to open the project. This will open the project in the IDE.
5. Add or Delete files as you need.
6. Investigate `config.toml` in the project directory. This is where you must specify your configurations for the project, including the toplevel module and GPIO pins.
7. Analyze, Synthesize, and Build your project.
8. After you have built a project, Generate the Bitstream for the project.
9. Download the bitstream to your computer. 
10. Use the FlashToFPGA GUI application to flash the bitstream to your FPGA. This application is [available here](https://github.com/Ellis-Brown/iceprog), and can be downloaded and run on your computer. This application is available for Windows, Mac, and Linux. You can also look into running the command line tool `iceprog` from `icestorm` to flash your FPGA, but this is not recommended.

### Buttons
The website has many features, so we are going to break them down more clearly by explaining what each button does. 

Show/Hide Options will display or hide 4 buttons: “Show Create Buttons”, “Show Delete Buttons”, “Show Build Buttons”, “Show Other Buttons”. Clicking on those 4 choices will lead to the buttons described below. 
 
#### Create Buttons
- New Project: To create a new project, click this button and enter your project name. If this project name already exists, a new project will not be created. Upon creation of a new project, there will already be a config.toml file in your project with the project name filled in. The new project will be displayed on the left side of the screen under the file tree.
- New File: To create a new file, click on the project in the file tree on the left side of the screen where you want the file to reside. Once you have clicked on the project name, click this button and enter your file name. If the file is a VHDL source file, its extension should be “.vhd”. Once you have created a new file it will be displayed in the file tree underneath the project and you can click on its name to open the file and start writing code.
#### Delete Buttons
- Delete Project: If you want to delete a project, click on the project name in the file tree and then click this button. Deleting a project completely removes it and you will not be able to recover it. 
- Delete File: If you want to delete a file, click on the file name in the file tree and then click this button. Deleting a file completely removes it and you will not be able to recover it. 
#### Build Buttons
- Analyze: If you want to analyze a file to check it for syntactic errors, you can click on this button. The output of the analysis will display in a box at the bottom of the screen. 
- Build: If you want to build a project, you can click on this button. It will generate a Makefile and pin constraints for the project based on the config.toml file. “make” will then be run on the source code and the output will be displayed in the box at the bottom of the screen. Build will also regenerate a netlist of the toplevel file each time it is run.
- Generate Bitstream: To create a .bin file for your project that can be flashed to the FPGA, click on this button. The .bin file will be saved under the project and if you click on the file in the file tree a “Download .bin” file button will appear on screen. This will download the bitstream so that you can flash it to the FPGA using the application described in the documentation.
- Synthesize: To create a netlist of a specific source code file, click on this button. A corresponding netlist file titled “filename-netlist.svg” will be generated and appear in the file tree. When this file is opened, you can view the netlist on the website. 

#### Other Buttons
- Save: If you want to save your file, you can either click on this button or use the Ctrl+S. There will be a save indicator next to the filename in the bar above the file output so that you can easily see if your project has been edited. If you have unsaved changes on your opened file and try to switch to another file there will be a prompt asking if you’d like to swap files. If you say yes, your changes will not be saved. If you say no, you have the chance to save your file before swapping. 
- Download Project: If you would like to download a project in order to have a copy locally on your computer, you can click on this button. A zip file titled with the project name will be downloaded onto your computer.

### Explanation of Sample Project
When you login to the website for the first time, you’ll notice there is a project already showing in your file tree. This is a sample project that will help you understand how to work with the website. Descriptions of each of the files are provided for you to reference as you begin working on your first ES4 projects. 

The overall project is titled adder and it contains the logic for the addition of three one-bit binary numbers. If you want to download a copy of this project and store it locally on your computer, you can click on the “Download Project” button (downloaded as “adder.zip”).

#### adder.vhd
- This file contains the source code for the adder project. There are 5 variables defined in the code (A, B, Cin, S, Cout). A, B, and Cin are the one-bit binary numbers being added together. S is the sum output and Cout is the carry bit. The code also defines all of the logic for the adder. 
If you analyze this file, there should be no errors.
#### config.toml
- This file contains the definition of the toplevel file and the source files. For this project the toplevel is “adder.vhd” and there is only one source file, which is also “adder.vhd”. If there were more source files, they would be placed in quotes within the src list separated by commas.
- The config file also contains the mappings of variables to FPGA pins. In this case, we had 5 variables that needed pin assignments. They can be defined by saying, “A = 26”. 
- When the project is built, if there are any problems with the config file, they will be displayed in the output box at the bottom of the screen.
####  adder-netlist.svg
- This file contains the corresponding netlist for the adder. When you open the file you can see the logic gates/hardware components/connections that are required to build the adder. This file can be generated by clicking on “adder.vhd” then clicking on the “synthesize” button or by clicking on the folder “adder” then clicking on the “build” button. 
####  pin_constraints.pcf
- You do not need to edit this file directly.
- This file is generated when you click on the build button. It contains the pin constraints based on the mappings defined in the config file. It will be regenerated every time you click on the build button 
####  adder.bin
- This file is generated when you click on the “Generate Bitstream” button. It is the binary file that contains the configuration information for the FPGA. 
You’ll notice that a download button appears on the screen when you click on this file. In order to flash the file to the FPGA, you must download “adder.bin” and then use the FPGA Flash Application that is described in the documentation.


### How to Flash Projects to FPGA from Website
To flash a project to your FPGA, you will need an FPGA, a wire to connect the FPGA to your computer, and a project that has been completely built. Please see how to build a project and assign pins in the workflow section of this documentation.

1. Build your project. Assign your pin configurations in `config.toml` in your project’s directory
2. Download the .bin file associated with your project. It should appear in the downloads folder of your computer.
3. Open up the FlashToFPGA application. 
    - On Windows, this will be in a folder based on where you installed it. See the [How to install FPGA flash](#https://github.com/Ellis-Brown/iceprog) documentation on the github page
    - On Mac, this should be in your applications folder on your computer. You should also be able to find this using Spotlight Search, by pressing Command + Space, then searching “FlashToFPGA.app”
    - On Ubuntu and other Linux platforms, this will be in a folder based on where you installed it. See the [How to install FPGA flash](#https://github.com/Ellis-Brown/iceprog) documentation on the github page
4. Select your downloaded bin file
5. Press the flash button
    - On both failure and success, make sure to read the log output in the flashing GUI screen
6. To update the FPGA, make a change on the website, rebuild the project, download the file, and select it before you attempt to flash again. Changes made on the website will not be reflected until you re-download the file.



## Project Structure
This explains how the project is structured, and how it is intended to be used. This section is not intended to be a user guide for the project.


### Dependencies
This project is intended to be hosted on the Tufts University Electrical Engineering and Computer Science Department's servers. As such, it is currently run in production using following setup
- Backend enviornment: Red Hat Enterprise Linux
- Every user is expected to have a user account on the server
    - accounts are in the form `/h/USERNAME`
- Every user has run the [installation script](bin/setup.sh) before using the web IDE

## Installation
This section is intended to be used by the Tufts University EECS admins, not by students. For students, please see [Usage](#Usage)

- Clone the repository
- Install the needed FPGA toolchains [TODO](#TODO)


### System Design
#### File Layout
- Frontend: HTML/CSS and Javascript. Found in [templates/index.html](templates/index.html) and [templates/layout.html](templates/layout.html).
- Backend: Flask server, found in [app.py](app.py)
    - Server is started by running `./run_server`, which can be found in [run_server](run_server). Make sure to make this script executable by first typing `chmod +x run_server`
- Database: None. The backend is the Tufts University EECS servers, which are used to store the user's files. If you were running this project outside of that enviornment, it is recommended you use a blobstore to store the user's files. See [Dependencies](#Dependencies) for more information on the EECS servers.

#### Request Handling
The frontend does `fetch()` requests to the backend for all resources, to save files, and open files. The backend processes these files directly on the file system, then serves them to the frontend. The frontend then renders the files as needed.



### Design Considerations
This project was built to circumvent using Lattice Radiant, which[ only is supported on Windows and Linux computers](https://www.latticesemi.com/LatticeRadiant?pr031521) at this time. Lattice Radiant is a featureful design suite for building and analyzing VHDL projects. This WebIDE excells at it's quick setup and ease of use. 


If your project grows larger than what can easily be handled in this website enviornment, the code is fully exportable to a new enviornment using Download Folder button on the website. A machine created `Makefile` can be run using the `make` command from the command line to build the project, and will build the full project as needed. However, you will need to install the needed build tools (ghdl, yosys). The code for generating this Makefile can be found in [app.py](app.py)


The backend uses a stateless request handling architecture, to help easily scale this project to appropriately handle load.



### Future enhancements
- It would be ideal to be able to flash code directly to the FPGA from the website. [Lots of endeavors were attempted to solve this problem](#TODO), but we ended unsuccessfully. If one were able to solve this problem, it would be greatly appreciated.

- A fully atonomously hosted version of this project would be ideal. Currently, the project is hosted on the Tufts EECS servers, and is not intended to be used outside of that environment. A easy to setup and use version of this website for an individual user, or with user sessions would be great for the open source community.


## Contributing
Contributions are welcome, but this repository is infrequently checked. If you would like to contribute, please open an issue or pull request.




## TODO
IF YOU WERE LINKED HERE, I MESSED UP. PLEASE LET ME KNOW SO I CAN FIX IT.