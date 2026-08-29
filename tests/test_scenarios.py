"""
Predefined Test Scenarios Suite - IPv6 Packet Processing Simulator (Phase 6)

This test module verifies the 5 core laboratory networking scenarios:
- Scenario 1: Successful Multi-Hop Delivery
- Scenario 2: Hop Limit Expiration Packet Drop
- Scenario 3: No Route to Host Packet Drop
- Scenario 4: Longest Prefix Match (LPM) Route Selection
- Scenario 5: Directly Connected Subnet Delivery
"""

import pytest
from src.forwarding import ForwardingStatus, forward_packet
from src.ipv6_packet import create_ipv6_packet
from src.network import NetworkTopology, build_sample_topology
from src.router import Router


class TestPredefinedScenarios:
    """Automated tests for the 5 standardized educational scenarios."""

    def test_scenario_1_successful_delivery(self):
        """
        Scenario 1: End-to-end packet delivery from Host A (2001:db8:1::10)
        to Host B (2001:db8:4::20) across 3 routers (R1 -> R2 -> R3).
        Expected Result: DELIVERED, Final Hop Limit = 61, 3 Routers Traversed.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Scenario 1: Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DELIVERED
        assert result.path == ["Host A", "R1", "R2", "R3", "Host B"]
        assert result.routers_traversed == ["R1", "R2", "R3"]
        assert result.num_router_hops == 3
        assert result.initial_hop_limit == 64
        assert result.final_hop_limit == 61

    def test_scenario_2_hop_limit_expiration(self):
        """
        Scenario 2: Packet sent with Hop Limit = 1 toward a remote subnet.
        Expected Result: DROPPED_HOP_LIMIT at Router R1 before forwarding.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Scenario 2: Low Hop Limit",
            next_header="UDP",
            hop_limit=1,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DROPPED_HOP_LIMIT
        assert "Hop Limit expired" in result.status_message
        assert result.routers_traversed == ["R1"]
        assert result.final_hop_limit == 1

    def test_scenario_3_no_route(self):
        """
        Scenario 3: Packet sent to an unroutable destination (2001:db8:99::10).
        Expected Result: DROPPED_NO_ROUTE at Router R1.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:99::10",
            payload="Scenario 3: Unroutable",
            next_header="UDP",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DROPPED_NO_ROUTE
        assert result.routers_traversed == ["R1"]
        assert "No matching route found" in result.status_message

    def test_scenario_4_longest_prefix_match(self):
        """
        Scenario 4: Router configured with overlapping routes (/32, /48, /64).
        Destination 2001:db8:4:10::20 must select /64 (the longest prefix).
        """
        router = Router("R_LPM")
        router.add_interface("eth0", "2001:db8:0::1/32")
        router.add_interface("eth1", "2001:db8:4::1/48")
        router.add_interface("eth2", "2001:db8:4:10::1/64")

        # Static overlapping routes
        router.add_static_route("2001:db8::/32", next_hop="2001:db8:10::1", interface="eth0")
        router.add_static_route("2001:db8:4::/48", next_hop="2001:db8:10::2", interface="eth1")
        router.add_static_route("2001:db8:4:10::/64", next_hop="2001:db8:10::3", interface="eth2")

        lookup = router.lookup_route("2001:db8:4:10::20")
        assert lookup["status"] == "SUCCESS"
        assert lookup["selected_prefix"] == "2001:db8:4:10::/64"
        assert lookup["next_hop"] == "2001:db8:10::3"
        assert lookup["interface"] == "eth2"
        assert len(lookup["matching_prefixes"]) == 3

    def test_scenario_5_direct_connected_delivery(self):
        """
        Scenario 5: Packet sent to a host on the same local subnet (2001:db8:1::25).
        Expected Result: DELIVERED directly with 0 router hops.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:1::25",
            payload="Scenario 5: Local Subnet",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DELIVERED
        assert result.num_router_hops == 0
        assert result.final_hop_limit == 64
        assert result.path == ["Host A", "Destination (2001:db8:1::25)"]
