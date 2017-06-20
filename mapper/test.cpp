#include "test_pch.hpp"

#define TEST BOOST_CHECK  // or BOOST_TEST with newer Boost than in Jessie

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

BOOST_AUTO_TEST_CASE(exitAndDoor_gmcpupdate_doorWins)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});  // initial GMCP
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}, {"open n;n", 123}});  // custom exit
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});  // second GMCP
	std::map<std::string, int> exits_12345_expected = {{"open n;n", 123}};
	TEST(m.getRoomExits(12345) == exits_12345_expected);
}

BOOST_AUTO_TEST_CASE(edgesRemoved)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}, {"e", 1234}});
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	std::map<std::string, int> exits_12345_expected = {{"n", 123}};
	TEST(m.getRoomExits(12345) == exits_12345_expected);
}

BOOST_AUTO_TEST_CASE(noParallelEdges)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}, {"open n;n", 123}});
	std::map<std::string, int> exits_12345_expected = {{"open n;n", 123}};
	TEST(m.getRoomExits(12345) == exits_12345_expected);

	m.addRoom(123, "My Room", "MyArea", {{"open s;s", 12345}, {"s", 12345}});
	std::map<std::string, int> exits_123_expected = {{"open s;s", 12345}};
	TEST(m.getRoomExits(123) == exits_123_expected);
}

BOOST_AUTO_TEST_CASE(readdRoom_exitDataPreserved)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	m.setExitData(12345, 123, "JSON blob with custom stuff");
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	TEST(m.getExitData(12345, 123) == "JSON blob with custom stuff");
}

BOOST_AUTO_TEST_CASE(noRoom_noExits_noCrash)
{
	Map m;
	TEST(m.getRoomExits(321) == (std::map<std::string, int>()));
}

BOOST_AUTO_TEST_CASE(setGetExitData)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	m.setExitData(12345, 123, "JSON blob with custom stuff");
	TEST(m.getExitData(12345, 123) == "JSON blob with custom stuff");
}

BOOST_AUTO_TEST_CASE(setGetMapData)
{
	Map m;
	m.setMapData("JSON blob with custom stuff");
	TEST(m.getMapData() == "JSON blob with custom stuff");
}

BOOST_AUTO_TEST_CASE(setGetRoomData)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	TEST(m.getRoomData(12345) == "MyArea");
	m.setRoomData(12345, "JSON blob with custom stuff");
	TEST(m.getRoomData(12345) == "JSON blob with custom stuff");
}

BOOST_AUTO_TEST_CASE(findRoomByName)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	m.addRoom(123, "room2", "area2", {{"s", 12345}});

	std::map<int, std::string> only = {{123, "room2"}};
	TEST(m.findRoomByName("oom2") == only);

	std::map<int, std::string> multi = {{123, "room2"}, {12345, "My Room"}};
	TEST(m.findRoomByName("oom") == multi);
}

BOOST_AUTO_TEST_CASE(insert_retrieve_retainsProperties)
{
	Map m;
	m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
	std::map<std::string, int> exits_12345_expected = {{"n", 123}};

	TEST(m.getRoomName(12345) == "My Room");
	TEST(m.getRoomData(12345) == "MyArea");
	TEST(m.getRoomExits(12345) == exits_12345_expected);
	std::tuple<int, int, int> xyz = std::make_tuple(0, 0, 0);
	std::tuple<int, int, int> xyz2 = std::make_tuple(0, 1, 0);
	TEST(m.getRoomCoords(12345) == xyz);

	m.addRoom(123, "room2", "area2", {{"s", 12345}});
	std::map<std::string, int> exits_123_expected = {{"s", 12345}};

	TEST(m.getRoomName(12345) == "My Room");
	TEST(m.getRoomData(12345) == "MyArea");
	TEST(m.getRoomExits(12345) == exits_12345_expected);
	TEST(m.getRoomCoords(12345) == xyz);

	TEST(m.getRoomName(123) == "room2");
	TEST(m.getRoomData(123) == "area2");
	TEST(m.getRoomExits(123) == exits_123_expected);
	TEST(m.getRoomCoords(123) == xyz2);
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
		m.addRoom(12345, "My Room", "MyArea", {{"n", 123}});
		m.addRoom(123, "room2", "area2", {{"s", 12345}});

		saved = m.serialize();
	}
	Map n(saved);

	TEST(n.getRoomName(12345) == "My Room");
	TEST(n.getRoomData(12345) == "MyArea");
	TEST(n.getRoomExits(12345) == exits_12345_expected);
	TEST(n.getRoomCoords(12345) == xyz);

	TEST(n.getRoomName(123) == "room2");
	TEST(n.getRoomData(123) == "area2");
	TEST(n.getRoomExits(123) == exits_123_expected);
	TEST(n.getRoomCoords(123) == xyz2);
}

namespace {
	using vec = std::vector<std::string>;
}

BOOST_AUTO_TEST_CASE(pathfinding)
{
	 /*   4
	  *  352|6
	  *   1
	  */
	Map m;
	m.addRoom(10, "Disjoint", "area2", {});
	m.addRoom(11, "southern", "area2", {{"n", 15}});
	m.addRoom(12, "eastern", "area2", {{"w", 15}, {"open e;e", 16}});
	m.addRoom(13, "western", "area2", {{"e", 15}});
	m.addRoom(14, "northern", "area2", {{"s", 15}});
	m.addRoom(15, "middle", "area2", {
			{"n", 14},
			{"e", 12},
			{"s", 11},
			{"w", 13}
			});
	m.addRoom(16, "door", "area2", {{"open w;w", 12}});

	for (int i = 11; i <= 16; ++i)
	{
		TEST(m.findPath(10, i) == vec({}));
		TEST(m.findPath(i, 10) == vec({}));
	}

	TEST(m.findPath(11, 11) == vec({}));
	TEST(m.findPath(11, 12) == vec({"n", "e"}));
	TEST(m.findPath(11, 13) == vec({"n", "w"}));
	TEST(m.findPath(11, 14) == vec({"n", "n"}));
	TEST(m.findPath(11, 15) == vec({"n"}));
	TEST(m.findPath(11, 16) == vec({"n", "e", "open e;e"}));

	TEST(m.findPath(12, 11) == vec({"w", "s"}));
	TEST(m.findPath(12, 12) == vec({}));
	TEST(m.findPath(12, 13) == vec({"w", "w"}));
	TEST(m.findPath(12, 14) == vec({"w", "n"}));
	TEST(m.findPath(12, 15) == vec({"w"}));
	TEST(m.findPath(12, 16) == vec({"open e;e"}));

	TEST(m.findPath(13, 11) == vec({"e", "s"}));
	TEST(m.findPath(13, 12) == vec({"e", "e"}));
	TEST(m.findPath(13, 13) == vec({}));
	TEST(m.findPath(13, 14) == vec({"e", "n"}));
	TEST(m.findPath(13, 15) == vec({"e"}));
	TEST(m.findPath(13, 16) == vec({"e", "e", "open e;e"}));

	TEST(m.findPath(14, 11) == vec({"s", "s"}));
	TEST(m.findPath(14, 12) == vec({"s", "e"}));
	TEST(m.findPath(14, 13) == vec({"s", "w"}));
	TEST(m.findPath(14, 14) == vec({}));
	TEST(m.findPath(14, 15) == vec({"s"}));
	TEST(m.findPath(14, 16) == vec({"s", "e", "open e;e"}));

	TEST(m.findPath(15, 11) == vec({"s"}));
	TEST(m.findPath(15, 12) == vec({"e"}));
	TEST(m.findPath(15, 13) == vec({"w"}));
	TEST(m.findPath(15, 14) == vec({"n"}));
	TEST(m.findPath(15, 15) == vec({}));
	TEST(m.findPath(15, 16) == vec({"e", "open e;e"}));

	TEST(m.findPath(16, 11) == vec({"open w;w", "w", "s"}));
	TEST(m.findPath(16, 12) == vec({"open w;w"}));
	TEST(m.findPath(16, 13) == vec({"open w;w", "w", "w"}));
	TEST(m.findPath(16, 14) == vec({"open w;w", "w", "n"}));
	TEST(m.findPath(16, 15) == vec({"open w;w", "w"}));
	TEST(m.findPath(16, 16) == vec({}));
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
		m.addRoom(i, "name", "data", exitsMap);
	}

	std::cout << "Graph of 50 rooms, 4 random exits in each room except for the first ones, generated in " << std::chrono::duration<double>(std::chrono::steady_clock::now() - checkpoint).count() << "s" << std::endl;
	checkpoint = std::chrono::steady_clock::now();

	for (int i = 0; i < 1000; ++i)
		m.findPath(i, 1000);

	std::cout << "a thousand random paths found in " << std::chrono::duration<double>(std::chrono::steady_clock::now() - checkpoint).count() << std::endl;
	checkpoint = std::chrono::steady_clock::now();
}
