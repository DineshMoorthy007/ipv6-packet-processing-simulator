"""
Unit tests for IPv6 Router, Interface Management, and Network Topology (Phase 3).
"""

import pytest
from src.router import Router, RouterInterface
from src.network import Host, Link, NetworkTopology, build_sample_topology


class TestRouterBasics:
    """Tests for Router initialization and interface management."""

    def test_router_creation(self):
        """Test basic router initialization."""
        r = Router("R1", "r1")
        assert r.name == "R1"
        assert r.router_id == "r1"
        assert len(r.interfaces) == 0
        assert len(r.routing_table) == 0

    def test_interface_creation_and_connected_route(self):
        """Test adding interface automatically creates connected route."""
        r = Router("R1")
        intf = r.add_interface("eth0", "2001:db8:1::1/64")

        assert intf.name == "eth0"
        assert intf.ip_address == "2001:db8:1::1"
        assert intf.network == "2001:db8:1::/64"
        assert intf.prefix_length == 64
        assert "eth0" in r.interfaces

        # Verify connected route was automatically registered in routing table
        routes = r.routing_table.routes
        assert len(routes) == 1
        assert routes[0].destination_prefix == "2001:db8:1::/64"
        assert routes[0].next_hop == "Direct"
        assert routes[0].interface == "eth0"
        assert routes[0].route_type == "Connected"

    def test_remove_interface_cleans_routes(self):
        """Test removing interface clears associated routes."""
        r = Router("R1")
        r.add_interface("eth0", "2001:db8:1::1/64")
        r.add_interface("eth1", "2001:db8:2::1/64")
        assert len(r.interfaces) == 2
        assert len(r.routing_table) == 2

        assert r.remove_interface("eth0") is True
        assert len(r.interfaces) == 1
        assert "eth0" not in r.interfaces
        assert len(r.routing_table) == 1
        assert r.routing_table.routes[0].interface == "eth1"


class TestRouterRouteLookup:
    """Tests for router route lookup, LPM, and next hop selection."""

    def test_connected_route_lookup(self):
        """Test route lookup for directly connected host."""
        r = Router("R1")
        r.add_interface("eth0", "2001:db8:1::1/64")

        res = r.lookup_route("2001:db8:1::10")
        assert res["status"] == "SUCCESS"
        assert res["selected_prefix"] == "2001:db8:1::/64"
        assert res["next_hop"] == "Direct"
        assert res["interface"] == "eth0"
        assert res["route_type"] == "Connected"

    def test_static_route_lookup(self):
        """Test route lookup for remote static network."""
        r = Router("R1")
        r.add_interface("eth0", "2001:db8:1::1/64")
        r.add_interface("eth1", "2001:db8:2::1/64")
        r.add_static_route("2001:db8:4::/64", next_hop="2001:db8:2::2", interface="eth1")

        res = r.lookup_route("2001:db8:4::20")
        assert res["status"] == "SUCCESS"
        assert res["selected_prefix"] == "2001:db8:4::/64"
        assert res["next_hop"] == "2001:db8:2::2"
        assert res["interface"] == "eth1"
        assert res["route_type"] == "Static"

    def test_no_route_condition(self):
        """Test lookup for unreachable destination returns NO_ROUTE."""
        r = Router("R1")
        r.add_interface("eth0", "2001:db8:1::1/64")

        res = r.lookup_route("2001:dead:beef::1")
        assert res["status"] == "NO_ROUTE"
        assert res["selected_route"] is None
        assert res["matching_routes"] == []

    def test_invalid_destination_address(self):
        """Test lookup with invalid destination IP string."""
        r = Router("R1")
        res = r.lookup_route("2001:invalid_addr::1")
        assert res["status"] == "INVALID_DESTINATION"
        assert res["is_valid"] is False

    def test_format_lookup_result(self):
        """Test format_lookup_result string structure."""
        r = Router("R1")
        r.add_interface("eth0", "2001:db8:1::1/64")
        r.add_interface("eth1", "2001:db8:2::1/64")
        r.add_static_route("2001:db8:4::/64", next_hop="2001:db8:2::2", interface="eth1")

        res = r.lookup_route("2001:db8:4::20")
        formatted = r.format_lookup_result(res)

        assert "ROUTE LOOKUP" in formatted
        assert "Router:\nR1" in formatted
        assert "Destination:\n2001:db8:4::20" in formatted
        assert "Matching Prefix:\n2001:db8:4::/64" in formatted
        assert "Selected Route:\n2001:db8:4::/64" in formatted
        assert "Next Hop:\n2001:db8:2::2" in formatted
        assert "Interface:\neth1" in formatted
        assert "Route Type:\nStatic" in formatted


class TestNetworkTopology:
    """Tests for NetworkTopology and sample 3-router network."""

    def test_sample_topology_building(self):
        """Test that build_sample_topology creates all routers, hosts, and links."""
        topo = build_sample_topology()
        assert len(topo.routers) == 3
        assert len(topo.hosts) == 2
        assert len(topo.links) == 4

        assert topo.get_router("R1") is not None
        assert topo.get_router("R2") is not None
        assert topo.get_router("R3") is not None
        assert topo.get_host("Host A") is not None
        assert topo.get_host("Host B") is not None

    def test_end_to_end_route_lookups_in_topology(self):
        """
        Verify that each router along the path from Host A to Host B has the correct next hop.
        Host A (2001:db8:1::10) -> R1 -> R2 -> R3 -> Host B (2001:db8:4::20)
        """
        topo = build_sample_topology()
        r1 = topo.get_router("R1")
        r2 = topo.get_router("R2")
        r3 = topo.get_router("R3")

        # Lookup on R1 for Host B
        r1_lookup = r1.lookup_route("2001:db8:4::20")
        assert r1_lookup["status"] == "SUCCESS"
        assert r1_lookup["next_hop"] == "2001:db8:2::2"  # R2 eth0
        assert r1_lookup["interface"] == "eth1"

        # Lookup on R2 for Host B
        r2_lookup = r2.lookup_route("2001:db8:4::20")
        assert r2_lookup["status"] == "SUCCESS"
        assert r2_lookup["next_hop"] == "2001:db8:3::2"  # R3 eth0
        assert r2_lookup["interface"] == "eth1"

        # Lookup on R3 for Host B
        r3_lookup = r3.lookup_route("2001:db8:4::20")
        assert r3_lookup["status"] == "SUCCESS"
        assert r3_lookup["next_hop"] == "Direct"  # Directly connected on eth1
        assert r3_lookup["interface"] == "eth1"
        assert r3_lookup["route_type"] == "Connected"

    def test_reverse_route_lookups_in_topology(self):
        """
        Verify reverse path lookups from Host B to Host A (2001:db8:1::10).
        """
        topo = build_sample_topology()
        r3 = topo.get_router("R3")
        r2 = topo.get_router("R2")
        r1 = topo.get_router("R1")

        # R3 -> Host A
        r3_lookup = r3.lookup_route("2001:db8:1::10")
        assert r3_lookup["next_hop"] == "2001:db8:3::1"  # R2 eth1
        assert r3_lookup["interface"] == "eth0"

        # R2 -> Host A
        r2_lookup = r2.lookup_route("2001:db8:1::10")
        assert r2_lookup["next_hop"] == "2001:db8:2::1"  # R1 eth1
        assert r2_lookup["interface"] == "eth0"

        # R1 -> Host A
        r1_lookup = r1.lookup_route("2001:db8:1::10")
        assert r1_lookup["next_hop"] == "Direct"
        assert r1_lookup["interface"] == "eth0"
