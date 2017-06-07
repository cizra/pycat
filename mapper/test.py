#!/usr/bin/env python3

import unittest
from libmapper import Map

class TestMapper(unittest.TestCase):
    def test_instantiate(self):
        m = Map("")

    def test_insert_retrieve_retainsProperties(self):
        m = Map("")
        m.addRoom(12345, "My Room", "My Area", {"n": 123})
        self.assertEqual(m.getRoomName(12345), "My Room")
        self.assertEqual(m.getRoomData(12345), "My Area")
        self.assertEqual(m.getRoomCoords(12345), (0, 0, 0))

        m.addRoom(123, "room2", "area2", {"s": 12345})
        self.assertEqual(m.getRoomName(12345), "My Room")
        self.assertEqual(m.getRoomData(12345), "My Area")
        self.assertEqual(m.getRoomCoords(12345), (0, 0, 0))
        self.assertEqual(m.getRoomName(123), "room2")
        self.assertEqual(m.getRoomData(123), "area2")
        self.assertEqual(m.getRoomCoords(123), (0, 1, 0))


    def test_serialize_deserialize_retainsProperties(self):
        m = Map("")
        m.addRoom(12345, "My Room", "My Area", {"n": 123})
        m.addRoom(123, "room2", "area2", {"s": 12345})
        ser = m.serialize()
        n = Map(ser)

        self.assertEqual(n.getRoomName(12345), "My Room")
        self.assertEqual(n.getRoomData(12345), "My Area")
        self.assertEqual(n.getRoomCoords(12345), (0, 0, 0))

        self.assertEqual(n.getRoomName(123), "room2")
        self.assertEqual(n.getRoomData(123), "area2")
        self.assertEqual(n.getRoomCoords(123), (0, 1, 0))

    def test_pathfinding(self):
        m = Map("")
        m.addRoom(12345, "My Room", "My Area", {"n": 123})
        m.addRoom(123, "room2", "area2", {"s": 12345})
        self.assertEqual(m.findPath(123, 12345), "s")

    def test_setGetMapData(self):
        m = Map()
        m.setMapData("foo bar")
        self.assertEqual(m.getMapData(), "foo bar")

    def test_setGetRoomData(self):
        m = Map("")
        m.addRoom(12345, "My Room", "My Area", {"n": 123})
        m.addRoom(123, "room2", "area2", {"s": 12345})
        self.assertEqual(m.getRoomData(12345), "My Area")
        self.assertEqual(m.getRoomData(123), "area2")


if __name__ == '__main__':
    unittest.main()
