#!/bin/bash
set -euo pipefail

# create a .iceprog-es4 directory in the home directory
mkdir -p ~/.iceprog-es4

home=$HOME

# Look at the architecture of the machine and download a binary based on mac vs linux (looking at uname)
if [[ $(uname) == "Darwin" ]]; then
    curl -L "https://raw.githubusercontent.com/Ellis-Brown/iceprog/main/iceprog" -o iceprog
else
    curl -L "https://raw.githubusercontent.com/Ellis-Brown/iceprog/main/linux-iceprog" -o iceprog
fi

# change permissions to make it executable
chmod +x iceprog

# move executable to the .iceprog-es4 directory
mv iceprog ~/.iceprog-es4/iceprog

# spit out a helpful message about adding to PATH based on the shell
if [[ $SHELL == "/bin/bash" ]]; then
    echo 'export PATH='$home'/.iceprog-es4:$PATH' >> "$home"/.bashrc
elif [[ $SHELL == "/bin/zsh" ]]; then
    echo 'export PATH='$home'/.iceprog-es4:$PATH' >> "$home"/.zshrc
elif [[ $SHELL == "/bin/tcsh" ]]; then
    echo 'setenv PATH '$home'/.iceprog-es4:$PATH' >> "$home"/.cshrc
else
    echo "Added "$home"/.iceprog-es4 to PATH. Please run 'source "$home"/.bashrc' or 'source "$home"/.zshrc' to update your PATH. 
          NOTE: If you are using a different shell, you will need to add the following to your shell's rc file:
          export PATH=$PATH:"$home"/.iceprog-es4
          "
fi

succ=0

# check for successful installation
if "$home"/.iceprog-es4/iceprog --help 2>/dev/null; then
    echo "iceprog installed successfully!"
    succ=1
else
    echo "iceprog failed to install. Please try again."
fi

if [[ $succ == 1 ]]; then
    echo "iceprog installed successfully! Please update your PATH by running 'source "$home"/.bashrc', 'source "$home"/.zshrc', or 'source "$home"/.cshrc' based on your shell."
else
    echo "iceprog failed to install. Please try again or contact Professor Bell."
fi