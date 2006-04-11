#!/bin/bash
CHECK=$1
SOURCE_DIR="sourceforge_website/"
REMOTE_USER="oubiwann"
REMOTE_HOST="shell.sourceforge.net"
REMOTE_DIR="pymon/"

if [ "$CHECK" = "check" ]; then
    echo
    echo "Hit ENTER to continue..."
    read
    echo "Performing a dry-run..."
    echo
   rsync \
    --recursive \
    --stats \
    --progress \
    --checksum \
    --dry-run \
    $SOURCE_DIR $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR
elif [ "$CHECK" = "download" ]; then
    echo
    echo "To download files from production, hit ENTER."
    echo "To quit now, hit ^C (Control-C)..."
    echo
    read
    echo "Downloading files from production..."
    echo
    rsync \
    --recursive \
    --stats \
    --progress \
    --checksum \
    $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR $SOURCE_DIR
else
    echo
    echo "To move files into production, hit ENTER."
    echo "To quit now, hit ^C (Control-C)..."
    echo
    read
    echo "Moving files into production..."
    echo
    rsync \
    --recursive \
    --stats \
    --progress \
    --checksum \
    $SOURCE_DIR $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR
fi
