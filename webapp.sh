#!/bin/sh

docker build --build-arg UID=`id -u` -t connectificator docker-webapp && docker run -it -p 1235:8888 -v `pwd`:/home/webserver/pycat connectificator
