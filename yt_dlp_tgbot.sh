#!/bin/bash
while true
do
    if ! pgrep -f "python3 yt_dlp_tgbot.py" > /dev/null
    then
        cd /root/
        exec python3 yt_dlp_tgbot.py &
    fi
    sleep 1
done
