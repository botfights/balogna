#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> liarsdice

python liarsdice.py tournament --log-level=10 $@
