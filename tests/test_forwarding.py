"""
Unit tests for IPv6 Packet Forwarding Simulation (Phase 4).
"""

import pytest
from src.forwarding import (
    ForwardingResult,
    ForwardingStatus,
    PacketForwarder,
    forward_packet,
)
from src.ipv6_packet import create_ipv6_packet
from src.network import build_sample_topology


class TestSuccessfulForwarding:
    """Tests for successful end-to-end multi-hop packet forwarding."""

    def test_successful_host_a_to_host_b_delivery(self):
        """
        Test that a packet sent from Host A (2001:db8:1::10) to Host B (2001:db8:4::20)
        successfully traverses R1 -> R2 -> R3 -> Host B with Hop Limit decrements.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        # 1. Verification of Status & Message
        assert result.status == ForwardingStatus.DELIVERED
        assert "delivered" in result.status_message.lower()

        # 2. Verification of Path
        expected_path = ["Host A", "R1", "R2", "R3", "Host B"]
        assert result.path == expected_path

        # 3. Verification of Routers Traversed & Hop Count
        assert result.routers_traversed == ["R1", "R2", "R3"]
        assert result.num_router_hops == 3

        # 4. Verification of Hop Limit Decrement: 64 -> 63 (R1) -> 62 (R2) -> 61 (R3)
        assert result.initial_hop_limit == 64
        assert result.final_hop_limit == 61
        assert pkt.hop_limit == 61

        # 5. Verification of Unchanged Fields
        assert pkt.source_address == "2001:db8:1::10"
        assert pkt.destination_address == "2001:db8:4::20"
        assert pkt.payload == "Hello IPv6"
        assert pkt.payload_length == 10
        assert pkt.next_header == 17
        assert pkt.next_header_name == "UDP"
        assert pkt.version == 6
        assert pkt.traffic_class == 0
        assert pkt.flow_label == 0

    def test_successful_reverse_path_host_b_to_host_a(self):
        """
        Test reverse path forwarding: Host B (2001:db8:4::20) -> Host A (2001:db8:1::10).
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:4::20",
            destination_address="2001:db8:1::10",
            payload="Reply from Host B",
            next_header="TCP",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host B")

        assert result.status == ForwardingStatus.DELIVERED
        assert result.path == ["Host B", "R3", "R2", "R1", "Host A"]
        assert result.routers_traversed == ["R3", "R2", "R1"]
        assert result.num_router_hops == 3
        assert result.final_hop_limit == 61


class TestHopLimitExpiration:
    """Tests for Hop Limit expiration and packet dropping."""

    def test_hop_limit_expires_at_first_router(self):
        """
        When Hop Limit = 1 at source, the packet must be dropped at the first router (R1).
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Expiring Packet",
            hop_limit=1,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DROPPED_HOP_LIMIT
        assert "Hop Limit expired" in result.status_message
        assert result.routers_traversed == ["R1"]
        assert result.path == ["Host A", "R1"]
        assert any("PACKET DROPPED" in entry for entry in result.log)

    def test_hop_limit_expires_mid_path(self):
        """
        When Hop Limit = 2 at source:
        - Reaches R1 (Hop Limit = 2 -> 1)
        - Reaches R2 (Hop Limit = 1 <= 1 -> Dropped at R2)
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Mid-Path Expiring Packet",
            hop_limit=2,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DROPPED_HOP_LIMIT
        assert result.routers_traversed == ["R1", "R2"]
        assert result.path == ["Host A", "R1", "R2"]


class TestNoRouteAndDropConditions:
    """Tests for unknown destination networks and unroutable packets."""

    def test_no_route_to_destination(self):
        """
        Destination 2001:db8:99::10 is not in R1's routing table.
        Packet must be dropped at R1 with DROPPED_NO_ROUTE.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:99::10",
            payload="Unknown Dest",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DROPPED_NO_ROUTE
        assert "No matching route" in result.status_message
        assert result.routers_traversed == ["R1"]
        assert any("No matching route found" in entry for entry in result.log)


class TestDirectSubnetDelivery:
    """Tests for direct local delivery without intermediate routing."""

    def test_direct_local_subnet_delivery(self):
        """
        When destination is on the exact same subnet as source host (2001:db8:1::/64),
        delivery occurs directly with 0 router hops.
        """
        topo = build_sample_topology()
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:1::25",
            payload="Local Subnet Ping",
            hop_limit=64,
        )

        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        assert result.status == ForwardingStatus.DELIVERED
        assert result.num_router_hops == 0
        assert result.final_hop_limit == 64
        assert result.path == ["Host A", "Destination (2001:db8:1::25)"]


class TestForwardingReportsAndSerialization:
    """Tests for report formatting, logs, and serialization."""

    def test_forwarding_result_to_dict(self):
        """Test dictionary serialization of ForwardingResult."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Test")
        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["status"] == "DELIVERED"
        assert data["num_router_hops"] == 3
        assert data["initial_hop_limit"] == 64
        assert data["final_hop_limit"] == 61
        assert len(data["log"]) > 0

    def test_format_report_output(self):
        """Test textual format_report contains all required visual sections."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Hello IPv6")
        result = forward_packet(packet=pkt, topology=topo, source_host_name="Host A")

        report = result.format_report()
        assert "IPv6 PACKET FORWARDING SIMULATION" in report
        assert "Packet Information:" in report
        assert "Source Address      : 2001:db8:1::10" in report
        assert "Destination Address : 2001:db8:4::20" in report
        assert "Forwarding Path:" in report
        assert "Host A" in report
        assert "R1" in report
        assert "R2" in report
        assert "R3" in report
        assert "Host B" in report
        assert "Forwarding Result:" in report
        assert "Status              : DELIVERED" in report
        assert "Routers Traversed   : 3 (R1, R2, R3)" in report
        assert "DETAILED FORWARDING EVENT LOG" in report
