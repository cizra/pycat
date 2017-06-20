#!/bin/sh

while inotifywait -q -e modify mapdraw; do
	clear
	cat mapdraw
done
