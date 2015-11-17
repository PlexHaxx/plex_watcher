# plex_watcher

A simple script to list who is accessing what and on what device.  Accesses your local plex media server.

Run it in a bash loop: ```while true; do python plex_watcher.py | tee -a plex_watcher.log; sleep 10; done```
