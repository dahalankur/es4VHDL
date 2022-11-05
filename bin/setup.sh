#!/bin/bash
# setup script
# After being a member of the appropriate group (es4vhdl for students), run this
# script to generate directories with appropriate permissions

set -euo pipefail

home_dir=/h/"$USER"

# create directory with appropriate group and permissions
mkdir -p "$home_dir"/.es4
chgrp es4vhdl "$home_dir"/.es4
chmod 2775 "$home_dir"/.es4