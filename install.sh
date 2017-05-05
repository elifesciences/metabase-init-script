#!/bin/bash
set -e # everything must succeed.
echo "[-] install.sh"

maxpy=/usr/bin/python3.5

# ll: python3.5
# http://stackoverflow.com/questions/2664740/extract-file-basename-without-path-and-extension-in-bash
py=${maxpy##*/} # magic

# check for exact version of python3
if [ ! -e "venv/bin/$py" ]; then
    echo "could not find venv/bin/$py, recreating venv"
    rm -rf venv
    virtualenv --python="$maxpy" venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "[✓] install.sh"
