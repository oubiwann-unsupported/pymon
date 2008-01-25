#!/bin/sh
echo
echo "Performing dry-run first ..."
echo
./admin/publishNews.py --dry-run -f sourceforge_website/newsItem
echo
echo "To publich news to SF.net, hit ENTER."
echo "To abort and edit, hit ^C (Control-C) ..."
echo
read
echo "Publishing to SF.net News ..."
./admin/publishNews.py -f sourceforge_website/newsItem
./admin/rsyncWebsite.sh
