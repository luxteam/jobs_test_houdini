#!/bin/bash
# sudo apt install gcc python-dev python3.5-dev python-pip
# sudo apt install python3-numpy python3-scipy
# apt install gcc python-dev
python3 get-pip.py
python3 -m pip install --upgrade pip wheel setuptools
python3 -m pip install --user -r requirements.txt
