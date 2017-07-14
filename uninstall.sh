#!/bin/sh

echo "Removing extension from ~/.efind/extensions"

for f in py-mail.py py-mail.pyc; do
	rm -f ~/.efind/extensions/$f
done
