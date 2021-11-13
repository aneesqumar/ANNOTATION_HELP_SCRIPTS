#!/usr/bin/env bash

echo 'creating conda environment....'
conda create --name multiviewer python=2.7
echo 'activate and install dependencies...'
source activate multiviewer
pip install -r requirements.txt
echo 'ready to go!'
