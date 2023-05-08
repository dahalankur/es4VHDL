## Platform Agnostic Web IDE for ICE40 FPGAs
> Capstone Project, Tufts Universtiy, 2023
> Sponsor: Professor Steven Bell of the EECS department at Tufts University

Developed by: [Ellis Brown](github.com/Ellis-Brown), [Alina Shah](github.com/gem-gray), [Ankur Dahal](github.com/dahalankur) Fall 2022-Spring 2023.


<img width="500" src="docs/images/VHDL-code.png" style="all: initial;align-items: center;  align-items: center;
  background-image: linear-gradient(144deg,#AF40FF, #5B42F3 50%,#00DDEB);
  border: 0;
  border-radius: 8px;
  box-shadow: rgba(151, 65, 252, 0.2) 0 15px 30px -5px;
  box-sizing: border-box;
  color: #FFFFFF;
  display: flex;
  font-family: Phantomsans, sans-serif;
  font-size: 20px;
  justify-content: center;
  line-height: 1em;
  max-width: 100%;
  min-width: 140px;
  padding: 3px;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  white-space: nowrap;
  cursor: pointer;
" alt="Web IDE example">

<img width="500" alt="Netlist Example" src="docs/images/Netlist.png" style="align-items: center;
  background-image: linear-gradient(144deg,#AF40FF, #5B42F3 50%,#00DDEB);
  border: 0;
  border-radius: 8px;
  box-shadow: rgba(151, 65, 252, 0.2) 0 15px 30px -5px;
  box-sizing: border-box;
  color: #FFFFFF;
  display: flex;
  font-family: Phantomsans, sans-serif;
  font-size: 20px;
  justify-content: center;
  line-height: 1em;
  max-width: 100%;
  min-width: 140px;
  padding: 3px;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  white-space: nowrap;
  cursor: pointer;">

<img width="300" alt="Config Example" src="docs/images/CONFIG.png" style="align-items: center;
  background-image: linear-gradient(144deg,#AF40FF, #5B42F3 50%,#00DDEB);
  border: 0;
  border-radius: 8px;
  box-shadow: rgba(151, 65, 252, 0.2) 0 15px 30px -5px;
  box-sizing: border-box;
  color: #FFFFFF;
  display: flex;
  font-family: Phantomsans, sans-serif;
  font-size: 20px;
  justify-content: center;
  line-height: 1em;
  max-width: 100%;
  min-width: 140px;
  padding: 3px;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  touch-action: manipulation;
  white-space: nowrap;
  cursor: pointer;">

## Table of contents
- [Project Description](#project-description)
- [Documentation](#documentation)
  - [Student User Documentation](docs/student-documentation.md)
  - [Maintainer Documentation](docs/maintainer-documentation.md)
- [Design Considerations](#design-considerations)
- [Future enhancements](#future-enhancements)
- [Contributing](#contributing)
 


## Project Description
This project builds a platform-agnostic web ide for ICE40 FPGAs. Users will be able to build projects, compile their code to bitstreams, , and flash their bitstreams to their FPGA all from the comfort of their web browser and a GUI application. This project is built using [Flask](https://flask.palletsprojects.com/en/2.0.x/) for the backend, and vanilla html and javascript for the frontend. To begin, please see [Student User Documentation](docs/student-documentation.md) for more information on how to use this website.

> This is intended to be used in combination with ES4 and other related courses at Tufts University which use VHDL and ice40 FPGAs. This is written with assumptions about the enviornment in which it runs. See [Maintainer Documentation](docs/images/maintainer-documentation.md) for more information.

#

## Documentation
- [Student User Documentation](docs/student-documentation.md)
- [Maintainer Documentation](docs/maintainer-documentation.md)
- [Attempting to flash directly from website (story)](docs/AttemptsToFlashLessons.md)

### Design Considerations
- This project was built to circumvent using Lattice Radiant, which[ only is supported on Windows and Linux computers](https://www.latticesemi.com/LatticeRadiant?pr031521) at this time. Lattice Radiant is a featureful design suite for building and analyzing VHDL projects. This WebIDE excells at it's quick setup and ease of use. 


- If your project grows larger than what can easily be handled in this website enviornment, the code is fully exportable to a new enviornment using Download Folder button on the website. A machine created `Makefile` can be run using the `make` command from the command line to build the project, and will build the full project as needed. However, you will need to install the needed build tools (ghdl, yosys). The code for generating this Makefile can be found in [app.py](app.py)


- The backend uses a stateless request handling architecture, to help easily scale this project to appropriately handle load.



### Future enhancements
- It would be ideal to be able to flash code directly to the FPGA from the website. [Lots of endeavors were attempted to solve this problem](#docs/AttempsToFlashLessons), but we ended unsuccessfully. If one were able to solve this problem, it would be greatly appreciated.

- A fully atonomously hosted version of this project would be ideal. Currently, the project is hosted on the Tufts EECS servers, and is not intended to be used outside of that environment. A easy to setup and use version of this website for an individual user, or with user sessions would be great for the open source community.


## Contributing
Contributions are welcome, but this repository is infrequently checked. If you would like to contribute, please open an issue or pull request. See [Future Enhancements](#future-enhancements) for ideas on what to contribute.



> Note: This project mentions and depends on a Flasher GUI, which can be on github at [github.com/Ellis-Brown/iceprog](github.com/Ellis-Brown/iceprog).
