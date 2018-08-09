#pragma once

#include <map>
#include <vector>
#include <string>

// MUD mapper
// Uses Boost's astar_search for pathfinding
class MapPimpl;
class Map {
	public:
		using mudId_t = int; // my favorite MUD uses large, sometimes negative integers as room IDs

		Map() : Map("") {}
		Map(std::string const& serialized);
		virtual ~Map();
		std::string serialize() const;

		// if room exists, updates its properties
		void addRoom(
				mudId_t room,
				std::string const& name,
				std::string const& data,
				std::map<std::string, mudId_t> const& exits
				);

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
		std::string getRoomName(mudId_t room) const;
		std::string getRoomData(mudId_t room) const;
		std::tuple<int, int, int> getRoomCoords(mudId_t room) const;
		std::map<std::string, mudId_t> getRoomExits(mudId_t room) const;

		// returns empty string if path wasn't found
		std::vector<std::string> findPath(mudId_t from, mudId_t to) const;

		std::string getExitData(mudId_t source, mudId_t target) const;
		void setExitData(mudId_t source, mudId_t target, std::string const& data);

	private:
		MapPimpl* d;
};
