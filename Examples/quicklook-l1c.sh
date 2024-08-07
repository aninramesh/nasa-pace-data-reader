#!/bin/bash

# add the path to the target directory as an argument using --target-dir with multiple directories separated by a space
# Example: ./quicklook-l1c.sh --target-dir /path/to/target/directory1 --save-path /path/to/target/directory-save

# autogenerate quicklooks for all *L1C.nc files in the target directory
autogenPy=/data/archive/ESI/HARP2/Software/quicklook/auto-image-gen-harp2.py

# file extension
ext="*L1C*5km.nc"

# Parse the command line arguments if no second argument is provided
if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --target-dir)
            target_dir="$2"
            shift
            shift
            ;;
        --save-path)
            dest_dir_="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# target_dir="/path/to/target/directory"
# argument --dest-dir is required
if [ -z "$target_dir" ]; then
    echo "The --target-dir argument is required"
    exit 1
fi

# Check if the target directory exists
if [ ! -d "$target_dir" ]; then
    echo "The target directory does not exist: $target_dir"
    exit 1
fi

# Check if the target directory is empty
if [ -z "$(ls -A $target_dir)" ]; then
    echo "The target directory is empty: $target_dir"
    exit 1
fi

# Check if the target directory contains any *L1C.nc files
if [ -z "$(find "$target_dir" -name "$ext")" ]; then
    echo "The target directory does not contain any *L1C.nc files: $target_dir"
    exit 1
fi

# destination directory
# Check if the target directory exists
if [ ! -d "$dest_dir_" ]; then
    echo "The save path does not exist: $dest_dir_"
    mkdir -p "$target_dir/quicklook"
else
    dest_dir=$dest_dir_
fi

# create the destination directory if it does not exist
mkdir -p "$dest_dir"

# Check if the destination directory exists
if [ ! -d "$dest_dir" ]; then
    echo "The destination directory does not exist: $dest_dir"
    exit 1
fi

# Check if the destination directory is empty
if [ -z "$(ls -A $dest_dir)" ]; then
    echo "The destination directory is empty: $dest_dir"
    echo "Destination directory will be used to store the quick looks and not empty"
fi


# List all *L1C.nc files in the target directory
# files=$(find "$target_dir" -name "*L1C.nc")
files=$(find "$target_dir" -name "$ext")

# Loop through each file
for file in $files; do

    # if file has already been processed, skip it (replace file(".nc") with file("_quicklook.png") to check if quick look exists)
    nfile=$(basename $file)
    nfile="${nfile%.*}"
    if [ -f "$dest_dir/$nfile""_quicklook.png" ]; then
        echo "$dest_dir/$nfile""_quicklook.png"
        echo "Quick look already exists: $file"
        continue
    else
        echo "---------------------------------------------"
        echo "$dest_dir/$nfile""_quicklook.png"
        echo "---------------------------------------------"
        echo "Creating quick look: $file"
        echo "Running: python $autogenPy --l1c_file $file --save_path $dest_dir"
        python $autogenPy --l1c_file $file --save_path $dest_dir 
        echo "---------------------------------------------"
        echo "---------------------------------------------"
    fi
done

