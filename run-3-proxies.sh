#!/bin/sh

RUN="/usr/bin/python3 ./pycat.py"

/usr/bin/tmux set remain-on-exit on
/usr/bin/tmux split-window -d -h -p 33 $RUN coffee 4002 grumpiest
sleep 1.5
/usr/bin/tmux split-window -d -h -p 33 $RUN coffee 4001 grumpier
sleep 1.5
$RUN coffee 4000 grumpy
