#!/bin/bash

# Set PYTHONPATH to the current directory
export PYTHONPATH=$(pwd)

# Run the chainlit command
chainlit run app/chat.py -w
