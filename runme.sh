#!/bin/sh

docker build -t pycat .
docker run -it -v `pwd`:/home/pycat/pycat pycat
