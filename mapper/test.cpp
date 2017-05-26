#include "mapper.hpp"

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE Mapper
#include <boost/test/unit_test.hpp>

#include <chrono>
#include <iostream>
#include <random>
#include <sstream>
#include <stack>

namespace std {
	std::ostream& operator<<(std::ostream& os, std::tuple<int, int, int> const& tpl)
	{
		unsigned x, y, z;
		std::tie(x, y, z) = tpl;
		return os << "tuple<" << x << "," << y << "," << z << ">";
	}
}

BOOST_AUTO_TEST_CASE(instantiate)
{
	Map m;
}

BOOST_AUTO_TEST_CASE(insert_retrieve_retainsProperties)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", "desert", {{"n", 123}});
	std::map<std::string, int> exits_12345_expected = {{"n", 123}};

	BOOST_TEST(m.getRoomName(12345) == "My Room");
	BOOST_TEST(m.getRoomZone(12345) == "MyArea");
	BOOST_TEST(m.getRoomTerrain(12345) == "desert");
	BOOST_TEST(m.getRoomExits(12345) == exits_12345_expected);
	std::tuple<int, int, int> xyz = std::make_tuple(0, 0, 0);
	std::tuple<int, int, int> xyz2 = std::make_tuple(0, 1, 0);
	BOOST_TEST(m.getRoomCoords(12345) == xyz);

	m.addRoom(123, "room2", "area2", "trn", {{"s", 12345}});
	std::map<std::string, int> exits_123_expected = {{"s", 12345}};

	BOOST_TEST(m.getRoomName(12345) == "My Room");
	BOOST_TEST(m.getRoomZone(12345) == "MyArea");
	BOOST_TEST(m.getRoomTerrain(12345) == "desert");
	BOOST_TEST(m.getRoomExits(12345) == exits_12345_expected);
	BOOST_TEST(m.getRoomCoords(12345) == xyz);

	BOOST_TEST(m.getRoomName(123) == "room2");
	BOOST_TEST(m.getRoomZone(123) == "area2");
	BOOST_TEST(m.getRoomTerrain(123) == "trn");
	BOOST_TEST(m.getRoomExits(123) == exits_123_expected);
	BOOST_TEST(m.getRoomCoords(123) == xyz2);
}

BOOST_AUTO_TEST_CASE(serialize_deserialize_retainsProperties)
{
	std::string saved;
	std::map<std::string, int> exits_12345_expected = {{"n", 123}};
	std::map<std::string, int> exits_123_expected = {{"s", 12345}};
	std::tuple<int, int, int> xyz = std::make_tuple(0, 0, 0);
	std::tuple<int, int, int> xyz2 = std::make_tuple(0, 1, 0);
	{
		Map m;
		m.addRoom(12345, "My Room", "MyArea", "desert", {{"n", 123}});
		m.addRoom(123, "room2", "area2", "trn", {{"s", 12345}});

		saved = m.serialize();
	}
	Map n(saved);

	BOOST_TEST(n.getRoomName(12345) == "My Room");
	BOOST_TEST(n.getRoomZone(12345) == "MyArea");
	BOOST_TEST(n.getRoomTerrain(12345) == "desert");
	BOOST_TEST(n.getRoomExits(12345) == exits_12345_expected);
	BOOST_TEST(n.getRoomCoords(12345) == xyz);

	BOOST_TEST(n.getRoomName(123) == "room2");
	BOOST_TEST(n.getRoomZone(123) == "area2");
	BOOST_TEST(n.getRoomTerrain(123) == "trn");
	BOOST_TEST(n.getRoomExits(123) == exits_123_expected);
	BOOST_TEST(n.getRoomCoords(123) == xyz2);
}

namespace map_internal {
	extern std::string stringify(std::vector<std::string> const& cmds);
	extern std::vector<std::string> runify(std::stack<std::string>&& cmds);
	extern std::string runifyDirs(std::vector<std::string> const& directions);
}

namespace {
	std::vector<std::string> crun(std::vector<std::string> const& in)
	{
		std::stack<std::string> fwd;
		for (const auto& s : in)
			fwd.push(s);
		return map_internal::runify(std::move(fwd));
	}
	using vec = std::vector<std::string>;
}

BOOST_AUTO_TEST_CASE(runifyDirs)
{
	BOOST_TEST(map_internal::runifyDirs({"n"}) == "n");
	BOOST_TEST(map_internal::runifyDirs({"n", "n"}) == "run 2n");
	BOOST_TEST(map_internal::runifyDirs({"n", "n", "n"}) == "run 3n");
	BOOST_TEST(map_internal::runifyDirs({"n", "e", "n"}) == "run n e n");
	BOOST_TEST(map_internal::runifyDirs({"n", "e", "e", "n"}) == "run n 2e n");
	BOOST_TEST(map_internal::runifyDirs({"n", "n", "e"}) == "run 2n e");
	BOOST_TEST(map_internal::runifyDirs({"n", "e", "e"}) == "run n 2e");
}

BOOST_AUTO_TEST_CASE(runify)
{
	// crashes BOOST_TEST(crun({}) == vec({}));
	BOOST_TEST(crun({"n"}) == vec({"n"}));
	BOOST_TEST(crun({"n", "n"}) == vec({"run 2n"}));
	BOOST_TEST(crun({"n", "n", "n", "e", "e"}) == vec({"run 2e 3n"}));
	BOOST_TEST(crun({"cmd"}) == vec({"cmd"}));
	BOOST_TEST(crun({"hi", "ho"}) == vec({"ho", "hi"}));
	BOOST_TEST(crun({"open n;n", "n", "n", "n", "e", "e", "open s;s"}) == vec({{"open s;s"}, {"run 2e 3n"}, {"open n;n"}}));
}

BOOST_AUTO_TEST_CASE(stringify)
{
	BOOST_TEST(map_internal::stringify({"n"}) == "n");
	BOOST_TEST(map_internal::stringify({"run 3n", "open n", "run 2n"}) == "run 3n;open n;run 2n");
}

BOOST_AUTO_TEST_CASE(pathfinding)
{
	 /*   4
	  *  352|6
	  *   1
	  */
	Map m;
	m.addRoom(10, "Disjoint", "area2", "trn", {});
	m.addRoom(11, "southern", "area2", "trn", {{"n", 15}});
	m.addRoom(12, "eastern", "area2", "trn", {{"w", 15}, {"open e;e", 16}});
	m.addRoom(13, "western", "area2", "trn", {{"e", 15}});
	m.addRoom(14, "northern", "area2", "trn", {{"s", 15}});
	m.addRoom(15, "middle", "area2", "trn", {
			{"n", 14},
			{"e", 12},
			{"s", 11},
			{"w", 13}
			});
	m.addRoom(16, "door", "area2", "trn", {{"open w;w", 12}});

	for (int i = 11; i <= 16; ++i)
	{
		BOOST_TEST(m.findPath(10, i) == "");
		BOOST_TEST(m.findPath(i, 10) == "");
	}

	BOOST_TEST(m.findPath(11, 11) == "");
	BOOST_TEST(m.findPath(11, 12) == "run n e");
	BOOST_TEST(m.findPath(11, 13) == "run n w");
	BOOST_TEST(m.findPath(11, 14) == "run 2n");
	BOOST_TEST(m.findPath(11, 15) == "n");
	BOOST_TEST(m.findPath(11, 16) == "run n e;open e;e");

	BOOST_TEST(m.findPath(12, 11) == "run w s");
	BOOST_TEST(m.findPath(12, 12) == "");
	BOOST_TEST(m.findPath(12, 13) == "run 2w");
	BOOST_TEST(m.findPath(12, 14) == "run w n");
	BOOST_TEST(m.findPath(12, 15) == "w");
	BOOST_TEST(m.findPath(12, 16) == "open e;e");

	BOOST_TEST(m.findPath(13, 11) == "run e s");
	BOOST_TEST(m.findPath(13, 12) == "run 2e");
	BOOST_TEST(m.findPath(13, 13) == "");
	BOOST_TEST(m.findPath(13, 14) == "run e n");
	BOOST_TEST(m.findPath(13, 15) == "e");
	BOOST_TEST(m.findPath(13, 16) == "run 2e;open e;e");

	BOOST_TEST(m.findPath(14, 11) == "run 2s");
	BOOST_TEST(m.findPath(14, 12) == "run s e");
	BOOST_TEST(m.findPath(14, 13) == "run s w");
	BOOST_TEST(m.findPath(14, 14) == "");
	BOOST_TEST(m.findPath(14, 15) == "s");
	BOOST_TEST(m.findPath(14, 16) == "run s e;open e;e");

	BOOST_TEST(m.findPath(15, 11) == "s");
	BOOST_TEST(m.findPath(15, 12) == "e");
	BOOST_TEST(m.findPath(15, 13) == "w");
	BOOST_TEST(m.findPath(15, 14) == "n");
	BOOST_TEST(m.findPath(15, 15) == "");
	BOOST_TEST(m.findPath(15, 16) == "e;open e;e");

	BOOST_TEST(m.findPath(16, 11) == "open w;w;run w s");
	BOOST_TEST(m.findPath(16, 12) == "open w;w");
	BOOST_TEST(m.findPath(16, 13) == "open w;w;run 2w");
	BOOST_TEST(m.findPath(16, 14) == "open w;w;run w n");
	BOOST_TEST(m.findPath(16, 15) == "open w;w;w");
	BOOST_TEST(m.findPath(16, 16) == "");
}

BOOST_AUTO_TEST_CASE(stress)
{
	return;
	auto checkpoint = std::chrono::steady_clock::now();
	std::random_device r;
	std::mt19937 gen(r());

	Map m;
	for (int i = 0; i < 50000; ++i) {
		std::uniform_int_distribution<> uniform(0, i);
		std::vector<int> exitDestinations;
		std::vector<std::string> exitNames = {"n", "e", "s", "w"};
		std::map<std::string, int> exitsMap;
		for (int j = 4; j --> 0;) {
			exitsMap[exitNames.back()] = uniform(gen);
			exitNames.pop_back();
		}
		m.addRoom(i, "name", "area", "terrain", exitsMap);
	}

	std::cout << "Graph of 50 rooms, 4 random exits in each room except for the first ones, generated in " << std::chrono::duration<double>(std::chrono::steady_clock::now() - checkpoint).count() << "s" << std::endl;
	checkpoint = std::chrono::steady_clock::now();

	for (int i = 0; i < 1000; ++i)
		m.findPath(i, 1000);

	std::cout << "a thousand random paths found in " << std::chrono::duration<double>(std::chrono::steady_clock::now() - checkpoint).count() << std::endl;
	checkpoint = std::chrono::steady_clock::now();
}
