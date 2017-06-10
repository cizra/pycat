#pragma once

#include "pytuple.hpp"

#include <map>
#include <string>

#include <boost/python.hpp>

// MUD mapper
// Uses Boost's astar_search for pathfinding
class MapPimpl;
class Map {
	public:
		using mudId_t = int; // my favorite MUD uses large, sometimes negative integers as room IDs

		Map() : Map("") {}
		Map(std::string const& serialized);
		~Map();
		std::string serialize() const;

		// TODO: write automagic converters like for tuple
		template <class K, class V>
		static boost::python::dict toPython(std::map<K, V> const& map) {
			boost::python::dict out;
			for (auto iter = map.begin(); iter != map.end(); ++iter)
				out[iter->first] = iter->second;
			return out;
		}

		template <class K, class V>
		static std::map<K, V> fromPython(boost::python::dict const& dict) {
			std::map<K, V> out;
			boost::python::list keys = dict.keys();
			for (int i = 0; i < len(keys); ++i) {
				boost::python::extract<K> extracted_key(keys[i]);
				assert(extracted_key.check());
				boost::python::extract<V> extracted_val(dict[keys[i]]);
				assert(extracted_val.check());
				out[extracted_key] = extracted_val;
			}
			return out;
		}


		// if room exists, updates its properties
		void addRoom(
				mudId_t room,
				std::string const& name,
				std::string const& data,
				std::map<std::string, mudId_t> const& exits
				);
		void addRoomPy(
				mudId_t room,
				std::string const& name,
				std::string const& data,
				boost::python::dict const& exits
				)
		{
			return addRoom(room, name, data, fromPython<std::string, int>(exits));
		}

		void setRoomData(mudId_t room, std::string const& data); // overwrites existing data
		// void setExitData(std::string const& data); -- possible to implement, if needed
		void setMapData(std::string const& data);
		std::string getMapData() const;

		// TODO: delete room

		// It might be that the map gets mapped starting from several different
		// places (think random teleports or portals). In that case, we'll need
		// to recalculate coordinates once the pieces have been joined.
		// void recalcRoomCoords(mudId_t startRoom);

		std::map<mudId_t, std::string> findRoomByName(std::string const& name) const;
		boost::python::dict findRoomByNameP(std::string const& name) const
		{
			return toPython(findRoomByName(name));
		}
		std::string getRoomName(mudId_t room) const;
		std::string getRoomData(mudId_t room) const;
		std::tuple<int, int, int> getRoomCoords(mudId_t room) const;
		std::map<std::string, mudId_t> getRoomExits(mudId_t room) const;
		boost::python::dict getRoomExitsP(mudId_t room) const
		{
			return toPython(getRoomExits(room));
		}

		// returns empty string if path wasn't found
		std::string findPath(mudId_t from, mudId_t to) const;

		std::string getExitData(mudId_t source, mudId_t target) const;
		void setExitData(mudId_t source, mudId_t target, std::string const& data);

	private:
		MapPimpl* d;
};

BOOST_PYTHON_MODULE(libmapper)
{
	export_cpptuple_conv();
	boost::python::class_<Map>("Map", boost::python::init<std::string>())
		.def(boost::python::init<>())
		.def("serialize", &Map::serialize)
		.def("addRoom", &Map::addRoomPy)
		.def("findPath", &Map::findPath)
		.def("getRoomName", &Map::getRoomName)
		.def("getRoomData", &Map::getRoomData)
		.def("getRoomCoords", &Map::getRoomCoords)
		.def("getRoomExits", &Map::getRoomExitsP)
		.def("setRoomData", &Map::setRoomData)
		.def("getRoomData", &Map::getRoomData)
		.def("setMapData", &Map::setMapData)
		.def("getMapData", &Map::getMapData)
		.def("setExitData", &Map::setExitData)
		.def("getExitData", &Map::getExitData)
		.def("findRoomByName", &Map::findRoomByNameP)
		;
}
