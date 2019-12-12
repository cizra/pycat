FROM alpine:latest
LABEL maintainer Elmo Todurov <elmo.todurov@eesti.ee>

RUN apk update && apk add build-base boost-dev alpine-sdk python3-dev socat
# RUN rm -f /var/cache/apk/*
RUN adduser -D pycat && addgroup pycat abuild && echo 'pycat ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
VOLUME /home/pycat/pycat

USER pycat
WORKDIR /home/pycat
ENV USER=pycat

EXPOSE 4000
CMD cd pycat/mapper && make test && cd .. && ./start_client.sh
