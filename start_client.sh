#!/bin/sh

LD_PRELOAD=libboost_serialization.so:libboost_python37.so:libpython3.7m.so::libstdc++.so.6:libmapper.so rlwrap ./pycat.py "${MODULE:-client}" "${ARG}"
