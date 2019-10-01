#!/bin/bash

fifo="/tmp/pycat-rlwrap-fifo"
if [ ! -f $fifo ]; then
	mkfifo $fifo
fi

tmux new-session \; \
  send-keys "./start_client.sh < $fifo" C-m \; \
  split-window -v -p 1 \; \
  send-keys "rlwrap tee $fifo" C-m \;
