#include "mapper.hpp"
#include <chrono>
#include <iostream>
#include <random>
#include <sstream>

namespace std {
	std::ostream& operator<<(std::ostream& os, std::tuple<int, int, int> const& tpl)
	{
		unsigned x, y, z;
		std::tie(x, y, z) = tpl;
		return os << "tuple<" << x << "," << y << "," << z << ">";
	}
}

int main()
{
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
