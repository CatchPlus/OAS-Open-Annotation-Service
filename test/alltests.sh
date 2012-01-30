#!/bin/bash

export LANG=en_US.UTF-8
export PYTHONPATH=.:$PYTHONPATH
python _alltests.py "$@"

