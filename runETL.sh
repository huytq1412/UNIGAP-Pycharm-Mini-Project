#!/bin/bash

# 1. Get the path of the folder containing this script (runETL.sh)
dir=$(dirname "$(realpath "$0")")

venv_path="$dir/.venv"
requirements_path="$dir/requirements.txt"

# 2. Check and create .venv if it doesn't exist
if [ ! -d "$venv_path" ]; then
    echo "Create venv"
    python3 -m venv "$venv_path"
fi

# 3. Install required libraries
echo "Install/update libraries from requirements.txt"
"$venv_path/bin/pip" install -r "$requirements_path"

# 4. Run file main.py
# Virtual environment path: $venv_path/bin/python
# main.py path: $dir/source/main.py
"$venv_path/bin/python" "$dir/source/main.py"
