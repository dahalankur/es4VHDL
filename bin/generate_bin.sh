#!/bin/bash

# Parameters:
# 1: The path of the file whose bitstream to be generated
set -euo pipefail

full_file=$1

file=$full_file
file=${file##*/} # remove the full path and just get the filename
entity=${file%.*} # remove the extension from the filename

# get the directory of the file and script
dir=${full_file%/*}

output_verilog="$dir"/"$entity".v
output_json="$dir"/"$entity".json
output_asc="$dir"/"$entity".asc
output_bin="$dir"/"$entity".bin
pcf_file="$dir"/pin_constraints.pcf

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

"$script_dir"/vhd2vl "$full_file" "$output_verilog"
"$script_dir"/fpga-toolchain/bin/yosys -p "synth_ice40 -top $entity -json $output_json" "$output_verilog"
"$script_dir"/fpga-toolchain/bin/nextpnr-ice40 --up5k --package sg48 --json "$output_json" --pcf "$pcf_file" --asc "$output_asc"
"$script_dir"/fpga-toolchain/bin/icepack "$output_asc" "$output_bin"

rm "$output_verilog" "$output_asc" "$output_json"
chmod 660 "$output_bin"