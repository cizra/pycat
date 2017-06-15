INCLUDEPATH += -isystem /usr/include/python3.6m
CXX = g++
LDFLAGS = -lboost_unit_test_framework -lboost_serialization -lboost_python3 -lpython3.6m
OPTFLAGS ?= -O0
CXXFLAGS += $(INCLUDEPATH) -c -std=c++14 -fPIC -Wall -Wextra -g $(OPTFLAGS)

.PHONY: all
all: libmapper.so test

mapper.o: mapper.cpp mapper.hpp pytuple.hpp
	$(CXX) $(CXXFLAGS) -o $@ mapper.cpp

test.o: test.cpp mapper.hpp pytuple.hpp
	$(CXX) $(CXXFLAGS) -o $@ test.cpp

libmapper.so: mapper.o
	$(CXX) -shared -o $@ $^

unittest: test.o libmapper.so
	$(CXX) -o $@ test.o -Wl,-rpath=`pwd` -L`pwd` -lmapper $(LDFLAGS)

.PHONY: test
test: unittest
	./unittest
	LD_PRELOAD=libboost_serialization.so:libboost_python3.so:libpython3.6m.so:libstdc++.so.6 ./test.py

.PHONY: clean
clean:
	rm -f libmapper.so mapper.o test.o unittest
