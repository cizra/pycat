INCLUDEPATH += -isystem /usr/include/python3.6m
CXX = g++
LDFLAGS = -lboost_unit_test_framework -lboost_serialization -lboost_python3 -lpython3.6m
OPTFLAGS ?= -O0
CXXFLAGS += $(INCLUDEPATH) -c -std=c++14 -fPIC -Wall -Wextra -g $(OPTFLAGS) -fmax-errors=1 -Winvalid-pch

.PHONY: all
all: libmapper.so test

test_pch.hpp.gch: test_pch.hpp mapper.hpp mapper_py.hpp pytuple.hpp
	$(CXX) $(CXXFLAGS) -o $@ test_pch.hpp

mapper_pch.hpp.gch: mapper_pch.hpp mapper.hpp
	$(CXX) $(CXXFLAGS) -o $@ mapper_pch.hpp

mapper_py_pch.hpp.gch: mapper_py_pch.hpp mapper_py.hpp mapper.hpp pytuple.hpp
	$(CXX) $(CXXFLAGS) -o $@ mapper_py_pch.hpp

mapper.o: mapper.cpp mapper.hpp pytuple.hpp mapper_pch.hpp.gch
	$(CXX) $(CXXFLAGS) -o $@ mapper.cpp

mapper_py.o: mapper_py.cpp mapper.hpp mapper_py.hpp pytuple.hpp mapper_py_pch.hpp.gch
	$(CXX) $(CXXFLAGS) -o $@ mapper_py.cpp

test.o: test.cpp mapper.hpp mapper_py.hpp pytuple.hpp test_pch.hpp.gch
	$(CXX) $(CXXFLAGS) -o $@ test.cpp

libmapper.so: mapper.o
	$(CXX) -shared -o $@ $^

libmapper_py.so: mapper_py.o mapper.o
	$(CXX) -shared -o $@ $^

unittest: test.o libmapper.so
	$(CXX) -o $@ test.o -Wl,-rpath=`pwd` -L`pwd` -lmapper $(LDFLAGS)

.PHONY: test
test: unittest libmapper.so libmapper_py.so
	LD_LIBRARY_PATH=`pwd` ./unittest
	LD_PRELOAD=libboost_serialization.so:libboost_python3.so:libpython3.6m.so:libstdc++.so.6 ./test.py

.PHONY: clean
clean:
	rm -f libmapper.so libmapper_py.so mapper.o mapper_py.o test.o unittest mapper_pch.hpp.gch test_pch.hpp.gch mapper_py_pch.hpp.gch
