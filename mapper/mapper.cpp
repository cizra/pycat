#include "mapper.hpp"

#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/graph/adj_list_serialize.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/astar_search.hpp>
#include <boost/serialization/vector.hpp>

#include <cmath>
#include <map>
#include <sstream>
#include <stack>
#include <string>
#include <vector>


namespace map_internal {
	struct graph_property {
		std::vector<std::string> terrains; // accumulates terrain types as they are encountered
		std::vector<std::string> zones; // accumulates zones as they are encountered

		template<class Archive>
		void serialize(Archive& ar, const unsigned int version)
		{
			(void)version;
			ar & terrains & zones;
		}
	};

	struct vertex_property {
		Map::mudId_t mudId;
		std::string name;
		size_t zone;
		size_t terrain;
		std::tuple<int, int, int> xyz;

		template<class Archive>
		void serialize(Archive& ar, const unsigned int version)
		{
			(void)version;
			ar & mudId & name & zone & terrain & std::get<0>(xyz) & std::get<1>(xyz) & std::get<2>(xyz);
		}
	};

	struct edge_property {
		std::string keyword;
		float weight;

		template<class Archive>
		void serialize(Archive& ar, const unsigned int version)
		{
			(void)version;
			ar & keyword;
		}
	};

	using mygraph_t = boost::adjacency_list<
		boost::vecS, // out edges for each vertex
		boost::vecS, // vertices
		boost::directedS,
		vertex_property,
		edge_property,
		graph_property,
		boost::vecS // edges
			>;

	size_t maybeInsert(std::string const& element, std::vector<std::string>& vec)
	{
		auto it = std::find(vec.begin(), vec.end(), element);
		if (it == vec.end())
			it = vec.emplace(it, element);
		return it - vec.begin();
	}

	std::tuple<int, int, int> coords(std::tuple<int, int, int> const& in, std::string const& dir)
	{
		int x, y, z;
		std::tie(x, y, z) = in;
		if (dir == "n")
			return std::make_tuple(x, y+1, z);
		if (dir == "e")
			return std::make_tuple(x+1, y, z);
		if (dir == "s")
			return std::make_tuple(x, y-1, z);
		if (dir == "w")
			return std::make_tuple(x-1, y, z);
		if (dir == "u")
			return std::make_tuple(x, y, z+1);
		if (dir == "d")
			return std::make_tuple(x, y, z-1);
		if (dir == "ne")
			return std::make_tuple(x+1, y+1, z);
		if (dir == "se")
			return std::make_tuple(x+1, y-1, z);
		if (dir == "sw")
			return std::make_tuple(x-1, y-1, z);
		if (dir == "nw")
			return std::make_tuple(x-1, y+1, z);
		return in;
	}

	bool direction(std::string const& cmd)
	{
		return cmd == "n" || cmd == "e" || cmd == "s" || cmd == "w" || cmd == "u" || cmd == "d";
	}

	std::string stringify(std::vector<std::string> const& cmds)
	{
		std::ostringstream out;
		bool first = true;
		for (const auto& s : cmds) {
			if (!first)
				out << ';';
			else
				first = false;
			out << s;
		}
		return out.str();
	}

	std::string runifyDirs(std::vector<std::string> const& directions)
	{
		assert(!directions.empty());
		int count = 1;
		// directions hold strings like {n n n e e s}. Transform them to 3n 2e s
		std::string str;
		bool first = true;
		for (size_t i = 1; i < directions.size(); ++i)
		{
			if (directions[i - 1] == directions[i]) {
				count++;
			} else {
				if (!first)
					str += ' ';
				else
					first = false;

				str += (count == 1 ? "" : std::to_string(count)) + directions[i - 1];
				count = 1;
			}
		}
		if (!first)
			str += ' ';
		str += (count == 1 ? "" : std::to_string(count)) + directions.back();
		if (str.size() == 1)
			return str;
		else
			return "run " + str;
	}

	std::vector<std::string> runify(std::stack<std::string>&& cmds)
	{
		// all directions are assmebled in the directions stack
		// when a non-direction is encountered, flush the accumulated directions (if any), and print that

		std::vector<std::string> out;
		out.reserve(cmds.size());
		std::vector<std::string> directions; // accumulates directions between non-directions
		directions.reserve(cmds.size());

		while (!cmds.empty()) {
			std::string const& current = cmds.top();
			if (direction(current)) {
				directions.emplace_back(cmds.top());
				cmds.pop();
			} else {
				if (!directions.empty()) {
					out.emplace_back(runifyDirs(directions));
					directions.clear();
				}
				out.emplace_back(cmds.top());
				cmds.pop();
			}
		}
		if (!directions.empty())
			out.emplace_back(runifyDirs(directions));
		return out;
	}
	
	std::stack<std::string> stackify(std::vector<mygraph_t::vertex_descriptor> const& predecessors, mygraph_t const& graph, mygraph_t::vertex_descriptor goal)
	{
		std::stack<std::string> reverse;
		for (auto v = goal;;) {
			auto pred = predecessors[v];
			if (pred == v)
				break;
			mygraph_t::edge_descriptor myEdge;
			bool found;
			std::tie(myEdge, found) = edge(predecessors[v], v, graph);
			assert(found);
			reverse.push(graph[myEdge].keyword);
			v = pred;
		}
		return reverse;
	}
}

using namespace map_internal;


class MapPimpl {
	public:
		mygraph_t graph;
		std::map<Map::mudId_t, mygraph_t::vertex_descriptor> ids; // mapping from arbitrary, possibly negative or stringy MUD-side IDs to small ints

		std::vector<std::string>& terrains;
		std::vector<std::string>& zones;

		MapPimpl()
			: terrains(graph[boost::graph_bundle].terrains)
			, zones(graph[boost::graph_bundle].zones)
		{}
};


Map::Map(std::string const& serialized)
	: d(new MapPimpl)
{
	if (serialized.empty())
		return;

	std::istringstream in(serialized);
	boost::archive::text_iarchive saved(in);
	saved >> d->graph;

	boost::graph_traits<mygraph_t>::vertex_iterator it, end;
	for (std::tie(it, end) = vertices(d->graph); it != end; ++it)
		d->ids[d->graph[*it].mudId] = *it;
}

Map::~Map()
{
	delete d;
}

std::string Map::serialize() const
{
	std::ostringstream out;
	boost::archive::text_oarchive saved(out);
	saved << d->graph;
	return out.str();
}

void Map::addRoom(Map::mudId_t room, std::string const& name, std::string const& zone_str, std::string const& terrain_str,
		std::map<std::string, Map::mudId_t> const& exits)
{
	size_t zone = maybeInsert(zone_str, d->zones);
	size_t terrain = maybeInsert(terrain_str, d->terrains);

	auto vertex_it = d->ids.find(room);

	bool inserted = false;
	if (vertex_it == d->ids.end())
	{
		vertex_it = d->ids.emplace(std::make_pair(room, add_vertex(d->graph))).first;
		inserted = true;
	}
	
	auto vertex_descriptor = vertex_it->second;

	d->graph[vertex_descriptor].mudId = room;
	d->graph[vertex_descriptor].name = name;
	d->graph[vertex_descriptor].zone = zone;
	d->graph[vertex_descriptor].terrain = terrain;
	// only the initial room gets inserted (plus random teleports, portals and stuff).
	// The rest get added as exits.
	if (inserted)
		d->graph[vertex_descriptor].xyz = std::make_tuple(0, 0, 0);

	clear_out_edges(vertex_descriptor, d->graph);
	for (auto exitKwDest : exits)
	{
		auto exit_vtx_it = d->ids.find(exitKwDest.second);
		if (exit_vtx_it == d->ids.end())
		{
			exit_vtx_it = d->ids.emplace(exitKwDest.second, add_vertex(d->graph)).first;
			d->graph[exit_vtx_it->second].mudId = exitKwDest.second;
			d->graph[exit_vtx_it->second].xyz = coords(
					d->graph[vertex_descriptor].xyz, exitKwDest.first);
		}
		add_edge(vertex_descriptor, exit_vtx_it->second, {exitKwDest.first, 1}, d->graph);
	}
}

std::string Map::getRoomName(Map::mudId_t room) const
{
	assert(d->ids.find(room) != d->ids.end());
	return d->graph[d->ids[room]].name;
}

std::string Map::getRoomZone(Map::mudId_t room) const
{
	assert(d->ids.find(room) != d->ids.end());
	return d->zones.at(d->graph[d->ids[room]].zone);
}

std::string Map::getRoomTerrain(Map::mudId_t room) const
{
	assert(d->ids.find(room) != d->ids.end());
	return d->terrains.at(d->graph[d->ids[room]].terrain);
}

std::tuple<int, int, int> Map::getRoomCoords(mudId_t room) const
{
	assert(d->ids.find(room) != d->ids.end());
	return d->graph[d->ids[room]].xyz;
}

std::map<std::string, Map::mudId_t> Map::getRoomExits(Map::mudId_t room) const
{
	assert(d->ids.find(room) != d->ids.end());

	std::map<std::string, Map::mudId_t> out;
	auto pair = out_edges(d->ids[room], d->graph);
	auto it = pair.first;
	auto end = pair.second;
	for (; it != end; ++it)
		out[d->graph[*it].keyword] = d->graph[target(*it, d->graph)].mudId;

	return out;
}

std::string Map::findPath(Map::mudId_t from, Map::mudId_t to, bool spaces) const
{
	(void)spaces;
	if (from == to)
		return "";

	assert(d->ids.find(from) != d->ids.end());
	assert(d->ids.find(to) != d->ids.end());

	std::vector<mygraph_t::vertex_descriptor> predecessors(num_vertices(d->graph));
	auto vertex = d->ids[from];
	auto goal = d->ids[to];
	int x1, y1, z1;
	std::tie(x1, y1, z1) = d->graph[vertex].xyz;
	auto heuristic = [this, x1, y1, z1](mygraph_t::vertex_descriptor vtx) {
		int x2, y2, z2;
		std::tie(x2, y2, z2) = d->graph[vtx].xyz;
		auto dx = x2 - x1;
		auto dy = y2 - y1;
		auto dz = z2 - z1;
		return ::sqrt(dx*dx + dy*dy + dz*dz);
	};

	// visitor that terminates when we find the goal
	struct found_goal {};
	class astar_goal_visitor : public boost::default_astar_visitor
	{
		public:
			astar_goal_visitor(mygraph_t::vertex_descriptor goal)
				: m_goal(goal)
			{}
			void examine_vertex(const mygraph_t::vertex_descriptor u, const mygraph_t& graph) const {
				(void)graph;
				if (u == m_goal)
					throw found_goal();
			}
		private:
			mygraph_t::vertex_descriptor m_goal;
	};

	try {
		std::vector<int> distances(num_vertices(d->graph));
		std::vector<int> costs(num_vertices(d->graph));
		astar_search(d->graph, vertex, heuristic,
				boost::predecessor_map(make_iterator_property_map(predecessors.begin(), get(boost::vertex_index, d->graph))).
				distance_map(make_iterator_property_map(distances.begin(), get(boost::vertex_index, d->graph))).
				weight_map(get(&edge_property::weight, d->graph)).
				visitor(astar_goal_visitor(goal))
				);
	} catch(const found_goal&) {
		return stringify(runify(stackify(predecessors, d->graph, goal)));
	}

	return "";
}
