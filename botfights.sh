#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> balogna

python balogna.py tournament --log-level=10 $@
