#!/bin/bash
SCRIPT_NAME="gitm.py"
COMMAND_NAME="gitm"
DESTINATION="/usr/local/bin"


echo "uninstalling $DESTINATION/$COMMAND_NAME" &&\
    sudo rm "$DESTINATION/$COMMAND_NAME" &&\
    echo "$COMMAND_NAME uninstalled"