FROM alpine:latest
LABEL maintainer Elmo Todurov <elmo.todurov@eesti.ee>

RUN apk update
RUN apk add build-base
RUN apk add boost-dev
RUN apk add alpine-sdk
RUN apk add python3-dev
RUN apk add sudo
# RUN rm -f /var/cache/apk/*
RUN adduser -D pycat && addgroup pycat abuild && echo 'pycat ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
VOLUME /home/pycat/pycat
COPY rlwrap_APKBUILD /home/pycat/rlwrap/APKBUILD
RUN chown -R pycat:pycat /home/pycat/rlwrap

USER pycat
WORKDIR /home/pycat
ENV USER=pycat
RUN abuild-keygen -n -a -i && cd rlwrap && abuild -r && find /home/pycat && sudo apk add /home/pycat/packages/pycat/x86_64/rlwrap-0.43-r0.apk
CMD cd pycat/mapper && make test && cd .. && ./start_client.sh
