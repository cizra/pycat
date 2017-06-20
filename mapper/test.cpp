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
	TEST(map_internal::runifyDirs({"n"}) == "n");
	TEST(map_internal::runifyDirs({"n", "n"}) == "run 2n");
	TEST(map_internal::runifyDirs({"n", "n", "n"}) == "run 3n");
	TEST(map_internal::runifyDirs({"n", "e", "n"}) == "run n e n");
	TEST(map_internal::runifyDirs({"n", "e", "e", "n"}) == "run n 2e n");
	TEST(map_internal::runifyDirs({"n", "n", "e"}) == "run 2n e");
	TEST(map_internal::runifyDirs({"n", "e", "e"}) == "run n 2e");
}

BOOST_AUTO_TEST_CASE(runify)
{
	// crashes TEST(crun({}) == vec({}));
	TEST(crun({"n"}) == vec({"n"}));
	TEST(crun({"n", "n"}) == vec({"run 2n"}));
	TEST(crun({"n", "n", "n", "e", "e"}) == vec({"run 2e 3n"}));
	TEST(crun({"cmd"}) == vec({"cmd"}));
	TEST(crun({"hi", "ho"}) == vec({"ho", "hi"}));
	TEST(crun({"open n;n", "n", "n", "n", "e", "e", "open s;s"}) == vec({{"open s;s"}, {"run 2e 3n"}, {"open n;n"}}));
}

BOOST_AUTO_TEST_CASE(stringify)
{
	TEST(map_internal::stringify({"n"}) == "n");
	TEST(map_internal::stringify({"run 3n", "open n", "run 2n"}) == "run 3n;open n;run 2n");
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
		TEST(m.findPath(10, i) == "");
		TEST(m.findPath(i, 10) == "");
	}

	TEST(m.findPath(11, 11) == "");
	TEST(m.findPath(11, 12) == "run n e");
	TEST(m.findPath(11, 13) == "run n w");
	TEST(m.findPath(11, 14) == "run 2n");
	TEST(m.findPath(11, 15) == "n");
	TEST(m.findPath(11, 16) == "run n e;open e;e");

	TEST(m.findPath(12, 11) == "run w s");
	TEST(m.findPath(12, 12) == "");
	TEST(m.findPath(12, 13) == "run 2w");
	TEST(m.findPath(12, 14) == "run w n");
	TEST(m.findPath(12, 15) == "w");
	TEST(m.findPath(12, 16) == "open e;e");

	TEST(m.findPath(13, 11) == "run e s");
	TEST(m.findPath(13, 12) == "run 2e");
	TEST(m.findPath(13, 13) == "");
	TEST(m.findPath(13, 14) == "run e n");
	TEST(m.findPath(13, 15) == "e");
	TEST(m.findPath(13, 16) == "run 2e;open e;e");

	TEST(m.findPath(14, 11) == "run 2s");
	TEST(m.findPath(14, 12) == "run s e");
	TEST(m.findPath(14, 13) == "run s w");
	TEST(m.findPath(14, 14) == "");
	TEST(m.findPath(14, 15) == "s");
	TEST(m.findPath(14, 16) == "run s e;open e;e");

	TEST(m.findPath(15, 11) == "s");
	TEST(m.findPath(15, 12) == "e");
	TEST(m.findPath(15, 13) == "w");
	TEST(m.findPath(15, 14) == "n");
	TEST(m.findPath(15, 15) == "");
	TEST(m.findPath(15, 16) == "e;open e;e");

	TEST(m.findPath(16, 11) == "open w;w;run w s");
	TEST(m.findPath(16, 12) == "open w;w");
	TEST(m.findPath(16, 13) == "open w;w;run 2w");
	TEST(m.findPath(16, 14) == "open w;w;run w n");
	TEST(m.findPath(16, 15) == "open w;w;w");
	TEST(m.findPath(16, 16) == "");
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
