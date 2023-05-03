#!/bin/bash
# setup script
# After being a member of the appropriate group (es4vhdl for students), run this
# script to generate directories with appropriate permissions

set -euo pipefail

home_dir=/h/"$USER"
server_project_dir=/h/adahal01/public_html/adder

# create directory with appropriate group and permissions
mkdir -p "$home_dir"/.es4
chgrp es4vhdl "$home_dir"/.es4
chmod 2775 "$home_dir"/.es4

# copy server_project_dir to home_dir/.es4
cp -r "$server_project_dir" "$home_dir"/.es4

# fix permissions of the copied directory
chgrp -R es4vhdl "$home_dir"/.es4/adder
chmod -R 2775 "$home_dir"/.es4/adder