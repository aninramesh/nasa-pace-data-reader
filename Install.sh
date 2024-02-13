#!/bin/bash
# Read the version from pyproject.toml
VERSION=$(awk -F'=' '/version/ {print $2}' pyproject.toml | tr -d ' "')

# Install current version
echo "Installing nasa_pace_data_reader version: ${VERSION}"

# Remove previous build
python3 -m pip uninstall nasa_pace_data_reader

# build the package
python3 -m build

# Run twine upload command
python3 -m twine upload --repository testpypi dist/*

# wait for 15 seconds
echo "Waiting for 15 seconds to make sure the package is uploaded to the test PyPI"
sleep 15

# Install nasa_pace_data_reader from test PyPI
echo "python3 -m pip install -i https://test.pypi.org/simple/ --no-deps nasa-pace-data-reader==${VERSION}"
python3 -m pip install -i https://test.pypi.org/simple/ --no-deps nasa-pace-data-reader==${VERSION}
