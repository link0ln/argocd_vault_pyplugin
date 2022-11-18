#!/usr/bin/env bash

sourcefile=python-helm-vault.py
binfile=python-helm-vault

python3 -m pip install cython

cython $sourcefile --embed

PYTHONLIBVER=python$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')$(python3-config --abiflags)

gcc -Os $(python3-config --includes) ${binfile}.c -o $binfile $(python3-config --ldflags) -l$PYTHONLIBVER
