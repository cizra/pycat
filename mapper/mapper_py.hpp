#pragma once

#include "mapper.hpp"
#include "pytuple.hpp"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>


// MUD mapper
// Uses Boost's astar_search for pathfinding
class MapPy : public Map {
	public:
		using Map::Map;

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


		void addRoomPy(
				mudId_t room,
				std::string const& name,
				std::string const& data,
				boost::python::dict const& exits
				);

		boost::python::dict findRoomByNameP(std::string const& name) const;

		boost::python::dict getRoomExitsP(mudId_t room) const;
};

BOOST_PYTHON_MODULE(libmapper_py)
{
	export_cpptuple_conv();
	boost::python::class_<std::vector<std::string>>("VectorOfStrings").def(boost::python::vector_indexing_suite<std::vector<std::string>>());

	boost::python::class_<MapPy>("Map", boost::python::init<std::string>())
		.def(boost::python::init<>())
		.def("serialize", &MapPy::serialize)
		.def("addRoom", &MapPy::addRoomPy)
		.def("findPath", &MapPy::findPath)
		.def("getRoomName", &MapPy::getRoomName)
		.def("getRoomData", &MapPy::getRoomData)
		.def("getRoomCoords", &MapPy::getRoomCoords)
		.def("getRoomExits", &MapPy::getRoomExitsP)
		.def("setRoomData", &MapPy::setRoomData)
		.def("getRoomData", &MapPy::getRoomData)
		.def("setMapData", &MapPy::setMapData)
		.def("getMapData", &MapPy::getMapData)
		.def("setExitData", &MapPy::setExitData)
		.def("getExitData", &MapPy::getExitData)
		.def("findRoomByName", &MapPy::findRoomByNameP)
		;
}
