#!/bin/sh

LD_PRELOAD=libboost_serialization.so:libboost_python3.so:libpython3.6m.so::libstdc++.so.6:libmapper.so rlwrap ./pycat.py client
