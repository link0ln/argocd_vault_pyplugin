#!/usr/bin/env bash

python3 -m pip install pyinstaller

pyinstaller python-helm-vault.py --onefile

cp ./dist/* ./
