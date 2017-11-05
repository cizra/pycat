FROM alpine:latest
LABEL maintainer Elmo Todurov <elmo.todurov@eesti.ee>

RUN apk update && apk add build-base boost-dev alpine-sdk python3-dev sudo uwsgi-python3
# RUN rm -f /var/cache/apk/*
# RUN adduser -D pycat && addgroup pycat abuild && echo 'pycat ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
RUN adduser -D webserver
EXPOSE 8887

USER webserver
WORKDIR /home/webserver
CMD cd pycat/mapper && export LD_PRELOAD=libboost_serialization.so:libboost_python3.so:libpython3.6m.so::libstdc++.so.6:libmapper.so && make test && cd .. && uwsgi --plugin python3 wsgi.json
