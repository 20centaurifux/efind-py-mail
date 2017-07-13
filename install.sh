#!/bin/sh

echo "Copying extension to ~/.efind/extensions"

mkdir -p ~/.efind/extensions && \
cp ./py-mail.py ~/.efind/extensions/
