#!/bin/sh

docker build -t pycat docker
docker run -it -v `pwd`:/home/pycat/pycat pycat
