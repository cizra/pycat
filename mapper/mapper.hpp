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
				std::string const& zone,
				std::string const& terrain,
				std::map<std::string, mudId_t> const& exits
				);
		void addRoomPy(
				mudId_t room,
				std::string const& name,
				std::string const& zone,
				std::string const& terrain,
				boost::python::dict const& exits
				)
		{
			return addRoom(room, name, zone, terrain, fromPython<std::string, int>(exits));
		}

		// TODO: delete room

		// It might be that the map gets mapped starting from several different
		// places (think random teleports or portals). In that case, we'll need
		// to recalculate coordinates once the pieces have been joined.
		// void recalcRoomCoords(mudId_t startRoom);

		std::string getRoomName(mudId_t room) const;
		std::string getRoomZone(mudId_t room) const;
		std::string getRoomTerrain(mudId_t room) const;
		std::tuple<int, int, int> getRoomCoords(mudId_t room) const;
		std::map<std::string, mudId_t> getRoomExits(mudId_t room) const;
		boost::python::dict getRoomExitsP(mudId_t room) const
		{
			return toPython(getRoomExits(room));
		}

		// spaces determines if the results looks like
		// run 2n e 2s w
		// or
		// run 2ne2sw
		// returns empty string if path wasn't found
		std::string findPath(mudId_t from, mudId_t to) const;

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
		.def("getRoomZone", &Map::getRoomZone)
		.def("getRoomTerrain", &Map::getRoomTerrain)
		.def("getRoomCoords", &Map::getRoomCoords)
		.def("getRoomExitsP", &Map::getRoomExits)
		;
}
