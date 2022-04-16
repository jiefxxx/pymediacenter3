#!/bin/sh

python3 -m pip install pyqt5
python3 -m pip install requests
python3 -m pip install requests-toolbelt
python3 -m pip install python-vlc
python3 setup.py install
cp -v pymediacenter.desktop /usr/share/applications/
cp -v pymediacenter.png  /usr/share/pixmaps/
