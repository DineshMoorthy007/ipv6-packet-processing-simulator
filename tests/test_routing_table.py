"""
Unit tests for IPv6 Routing Table and Longest Prefix Match (Phase 3).
"""

import pytest
from src.routing_table import Route, RoutingTable


class TestRouteCreation:
    """Tests for Route instantiation and validation."""

    def test_valid_connected_route(self):
        """Test creating a connected route."""
        route = Route(
            destination_prefix="2001:db8:1::/64",
            next_hop=None,
            interface="eth0",
            route_type="Connected",
        )
        assert route.destination_prefix == "2001:db8:1::/64"
        assert route.prefix_length == 64
        assert route.next_hop == "Direct"
        assert route.interface == "eth0"
        assert route.route_type == "Connected"

    def test_valid_static_route(self):
        """Test creating a static route with next hop."""
        route = Route(
            destination_prefix="2001:db8:4::/64",
            next_hop="2001:db8:2::2",
            interface="eth1",
            route_type="Static",
        )
        assert route.destination_prefix == "2001:db8:4::/64"
        assert route.next_hop == "2001:db8:2::2"
        assert route.interface == "eth1"
        assert route.route_type == "Static"

    def test_invalid_destination_prefix(self):
        """Test rejection of malformed destination prefix."""
        with pytest.raises(ValueError, match="Invalid IPv6 destination prefix"):
            Route(
                destination_prefix="2001:invalid_net:::1/64",
                next_hop="Direct",
                interface="eth0",
            )

    def test_invalid_next_hop_for_static_route(self):
        """Test rejection of invalid next hop address."""
        with pytest.raises(ValueError, match="Invalid Next Hop IPv6 address"):
            Route(
                destination_prefix="2001:db8:4::/64",
                next_hop="invalid_ip",
                interface="eth1",
                route_type="Static",
            )


class TestRoutingTableOperations:
    """Tests for RoutingTable add, remove, and query operations."""

    def test_add_single_route(self):
        """Test adding a single route."""
        rt = RoutingTable()
        r = rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")
        assert len(rt) == 1
        assert r.destination_prefix == "2001:db8:1::/64"

    def test_add_multiple_routes(self):
        """Test adding multiple routes."""
        rt = RoutingTable()
        rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")
        rt.add_route("2001:db8:2::/64", "Direct", "eth1", "Connected")
        rt.add_route("2001:db8:4::/64", "2001:db8:2::2", "eth1", "Static")
        assert len(rt) == 3

    def test_remove_route(self):
        """Test removing a route by prefix."""
        rt = RoutingTable()
        rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")
        rt.add_route("2001:db8:2::/64", "Direct", "eth1", "Connected")

        assert rt.remove_route("2001:db8:1::/64") is True
        assert len(rt) == 1
        assert rt.remove_route("2001:db8:99::/64") is False

    def test_matching_destination(self):
        """Test finding matching routes for a destination."""
        rt = RoutingTable()
        rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")
        rt.add_route("2001:db8:2::/64", "Direct", "eth1", "Connected")

        matches = rt.get_matching_routes("2001:db8:1::10")
        assert len(matches) == 1
        assert matches[0].destination_prefix == "2001:db8:1::/64"

    def test_no_matching_route(self):
        """Test query for destination with no route returns empty list and None."""
        rt = RoutingTable()
        rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")

        matches = rt.get_matching_routes("2001:db8:99::10")
        assert matches == []
        assert rt.find_best_route("2001:db8:99::10") is None


class TestLongestPrefixMatch:
    """Tests for Longest Prefix Match (LPM) logic."""

    def test_longest_prefix_match_tie_breaking(self):
        """
        Given multiple overlapping prefixes:
        - 2001:db8::/32
        - 2001:db8:4::/48
        - 2001:db8:4:10::/64
        For destination 2001:db8:4:10::20, the /64 route must be selected.
        """
        rt = RoutingTable()
        rt.add_route("2001:db8::/32", "2001:db8:10::1", "eth0", "Static")
        rt.add_route("2001:db8:4::/48", "2001:db8:10::2", "eth1", "Static")
        rt.add_route("2001:db8:4:10::/64", "2001:db8:10::3", "eth2", "Static")

        matches = rt.get_matching_routes("2001:db8:4:10::20")
        assert len(matches) == 3

        # Must be ordered by prefix length descending
        assert matches[0].prefix_length == 64
        assert matches[1].prefix_length == 48
        assert matches[2].prefix_length == 32

        # Best route must be /64
        best = rt.find_best_route("2001:db8:4:10::20")
        assert best is not None
        assert best.destination_prefix == "2001:db8:4:10::/64"
        assert best.next_hop == "2001:db8:10::3"
        assert best.interface == "eth2"

    def test_longest_prefix_match_fallback_to_shorter(self):
        """
        Destination matching /48 but not /64 falls back to /48.
        """
        rt = RoutingTable()
        rt.add_route("2001:db8::/32", "2001:db8:10::1", "eth0", "Static")
        rt.add_route("2001:db8:4::/48", "2001:db8:10::2", "eth1", "Static")
        rt.add_route("2001:db8:4:10::/64", "2001:db8:10::3", "eth2", "Static")

        # 2001:db8:4:20::1 matches /32 and /48, but not /64
        best = rt.find_best_route("2001:db8:4:20::1")
        assert best is not None
        assert best.destination_prefix == "2001:db8:4::/48"
        assert best.next_hop == "2001:db8:10::2"


class TestRoutingTableDisplay:
    """Tests for table formatting and output."""

    def test_display_table_output(self):
        """Test ASCII table output contains headers and formatted rows."""
        rt = RoutingTable()
        rt.add_route("2001:db8:1::/64", "Direct", "eth0", "Connected")
        rt.add_route("2001:db8:2::/64", "Direct", "eth1", "Connected")
        rt.add_route("2001:db8:4::/64", "2001:db8:2::2", "eth1", "Static")

        display = rt.display_table()
        assert "Destination Prefix" in display
        assert "Next Hop" in display
        assert "Interface" in display
        assert "Type" in display
        assert "2001:db8:1::/64" in display
        assert "Direct" in display
        assert "2001:db8:4::/64" in display
        assert "2001:db8:2::2" in display
