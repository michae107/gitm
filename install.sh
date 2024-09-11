#!/bin/bash
SCRIPT_NAME="gitm.py"
COMMAND_NAME="gitm"
DESTINATION="/usr/local/bin"


echo "installing to $DESTINATION/$COMMAND_NAME" &&\
    sudo ln -sf "$(pwd)/$SCRIPT_NAME" "$DESTINATION/$COMMAND_NAME" &&\
    chmod +x "$SCRIPT_NAME" &&\
    echo "$COMMAND_NAME installed"