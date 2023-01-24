#!/bin/bash

# Parameters:
# 1: The filepath to the be synthesized
set -euo pipefail

full_file=$1

file=$full_file
file=${file##*/} # remove the full path and just get the filename
entity=${file%.*} # remove the extension from the filename

output=$entity.json

# get the directory of the file and script
dir=${full_file%/*}
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ghdl -a --std=08 $full_file
"$script_dir"/fpga-toolchain/bin/yosys -p "ghdl --std=08 $entity; prep -top $entity; write_json -compat-int $output"
node "$script_dir"/node_modules/netlistsvg/bin/netlistsvg.js $output -o "$dir"/$entity-netlist.svg
chmod 660 "$dir"/$entity-netlist.svg
rm $output