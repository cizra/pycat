#include "mapper_py_pch.hpp"

void MapPy::addRoomPy(
    mudId_t room,
    std::string const& name,
    std::string const& data,
    boost::python::dict const& exits
    )
{
  return addRoom(room, name, data, fromPython<std::string, int>(exits));
}

boost::python::dict MapPy::findRoomByNameP(std::string const& name) const
{
  return toPython(findRoomByName(name));
}

boost::python::dict MapPy::getRoomExitsP(mudId_t room) const
{
  return toPython(getRoomExits(room));
}
