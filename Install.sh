#!/bin/bash
# Read the version from pyproject.toml
VERSION=$(awk -F'=' '/version/ {print $2}' pyproject.toml | tr -d ' "')

# Which Repository to upload
repo="pypi" # testpypi or pypi

# Install current version
echo "Installing nasa_pace_data_reader version: ${VERSION}"

# Remove previous build
python3 -m pip uninstall nasa_pace_data_reader

# build the package
python3 -m build

# check which repository to upload
if [ $repo = "testpypi" ]; then
    echo "Uploading to test PyPI"
else
    echo "Uploading to PyPI"
fi
# Run twine upload command
python3 -m twine upload --repository ${repo} dist/*

# wait for 15 seconds
echo "Waiting for 5 seconds to make sure the package is uploaded to the ${repo}..."
sleep 5

# Install nasa_pace_data_reader from test PyPI
echo "Installing nasa_pace_data_reader from ${repo}"
echo "Run the following command to install the package"
echo "---------------------------------------------"
if [ $repo = "testpypi" ]; then
    echo "python3 -m pip install -i https://test.pypi.org/simple/ nasa-pace-data-reader==${VERSION}"
else
    echo "python3 -m pip install nasa-pace-data-reader==${VERSION}"
fi

