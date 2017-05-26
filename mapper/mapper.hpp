#pragma once

#include <map>
#include <string>

// MUD mapper
// Uses Boost's astar_search for pathfinding
class MapPimpl;
class Map {
	public:
		using mudId_t = int; // my favorite MUD uses large, sometimes negative integers as room IDs

		Map();
		~Map();
		Map(std::string const& serialized);
		std::string serialize() const;

		// if room exists, updates its properties
		void addRoom(
				mudId_t room,
				const char* name,
				const char* zone,
				const char* terrain,
				std::map<std::string, mudId_t> const& exits
				);

		// If targetRoom doesn't exist, creates it
		void addExit(mudId_t room, const char* dir, mudId_t targetRoom);

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

		// spaces determines if the results looks like
		// run 2n e 2s w
		// or
		// run 2ne2sw
		// returns empty string if path wasn't found
		std::string findPath(mudId_t from, mudId_t to, bool spaces=true) const;

	private:
		MapPimpl* d;
};
