#!/bin/bash

LD_PRELOAD=libboost_serialization.so:libboost_python-py35.so:libpython3.5m.so rlwrap ./pycat.py client
