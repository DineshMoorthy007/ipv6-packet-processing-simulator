"""
Unit tests for Network Visualization and Simulation Dashboard (Phase 5).
"""

import pytest
from src.forwarding import forward_packet
from src.ipv6_packet import create_ipv6_packet
from src.network import build_sample_topology
from src.visualization import NetworkVisualizer


class TestNetworkGraphData:
    """Tests for topology graph data structure and extraction."""

    def test_get_topology_graph_data_nodes_and_edges(self):
        """Test extraction of nodes, edges, and subnets from topology."""
        topo = build_sample_topology()
        data = NetworkVisualizer.get_topology_graph_data(topo)

        assert "nodes" in data
        assert "edges" in data
        assert "active_path" in data

        # Check nodes
        node_ids = [n["id"] for n in data["nodes"]]
        assert "Host A" in node_ids
        assert "Host B" in node_ids
        assert "R1" in node_ids
        assert "R2" in node_ids
        assert "R3" in node_ids

        # Check edges
        assert len(data["edges"]) == 4
        edge_subnets = [e["network"] for e in data["edges"]]
        assert "2001:db8:1::/64" in edge_subnets
        assert "2001:db8:2::/64" in edge_subnets
        assert "2001:db8:3::/64" in edge_subnets
        assert "2001:db8:4::/64" in edge_subnets

    def test_graph_data_with_active_path(self):
        """Test that active path flags are correctly set in nodes and edges."""
        topo = build_sample_topology()
        active_path = ["Host A", "R1", "R2", "R3", "Host B"]
        data = NetworkVisualizer.get_topology_graph_data(topo, active_path=active_path)

        for node in data["nodes"]:
            assert node["is_active"] is True

        for edge in data["edges"]:
            assert edge["is_active"] is True


class TestDeviceInformationFormatting:
    """Tests for Host and Router device information cards."""

    def test_host_details_card(self):
        """Test host card contains IP, network, gateway, interface."""
        topo = build_sample_topology()
        card = NetworkVisualizer.format_device_details("Host A", topo)

        assert "HOST INFORMATION" in card
        assert "Host A" in card
        assert "2001:db8:1::10/64" in card
        assert "2001:db8:1::/64" in card
        assert "2001:db8:1::1" in card
        assert "eth0" in card

    def test_router_details_card(self):
        """Test router card contains interfaces and routing table."""
        topo = build_sample_topology()
        card = NetworkVisualizer.format_device_details("R1", topo)

        assert "ROUTER INFORMATION" in card
        assert "R1" in card
        assert "eth0" in card
        assert "eth1" in card
        assert "2001:db8:1::/64" in card
        assert "2001:db8:2::/64" in card
        assert "Active Routing Table:" in card

    def test_unknown_device_handling(self):
        """Test query for non-existent device returns clean error message."""
        topo = build_sample_topology()
        res = NetworkVisualizer.format_device_details("NonExistentDevice", topo)
        assert "Error: Device 'NonExistentDevice' not found" in res


class TestForwardingVisualization:
    """Tests for packet movement snapshots, timeline, and statistics formatting."""

    def test_format_packet_movement_steps_successful(self):
        """Test step-by-step movement snapshots generation."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Movement Test")
        res = forward_packet(pkt, topo, source_host_name="Host A")

        steps = NetworkVisualizer.format_packet_movement_steps(res)
        assert len(steps) == 5  # Host A, R1, R2, R3, Host B

        assert "Step 1 of 5" in steps[0]
        assert ">>> [Host A] <<<" in steps[0]
        assert "Hop Limit        : 64" in steps[0]

        assert "Step 2 of 5" in steps[1]
        assert ">>> [R1] <<<" in steps[1]

        assert "Step 5 of 5" in steps[4]
        assert ">>> [Host B] <<<" in steps[4]
        assert "PACKET DELIVERED SUCCESSFULLY" in steps[4]

    def test_format_forwarding_timeline_successful(self):
        """Test timeline generation for successful packet delivery."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Timeline Test")
        res = forward_packet(pkt, topo, source_host_name="Host A")

        timeline = NetworkVisualizer.format_forwarding_timeline(res)
        assert "PACKET PROCESSING TIMELINE" in timeline
        assert "Packet created at Host A" in timeline
        assert "Packet received by R1" in timeline
        assert "R1 selected route" in timeline
        assert "Packet delivered to Host B" in timeline
        assert "PACKET DELIVERED SUCCESSFULLY" in timeline

    def test_format_forwarding_timeline_dropped(self):
        """Test timeline generation for dropped packet."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", hop_limit=1)
        res = forward_packet(pkt, topo, source_host_name="Host A")

        timeline = NetworkVisualizer.format_forwarding_timeline(res)
        assert "PACKET PROCESSING TIMELINE" in timeline
        assert "Hop Limit expired" in timeline
        assert "PACKET DROPPED" in timeline

    def test_format_forwarding_stats(self):
        """Test forwarding statistics table formatting."""
        topo = build_sample_topology()
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Stats Test")
        res = forward_packet(pkt, topo, source_host_name="Host A")

        stats = NetworkVisualizer.format_forwarding_stats(res)
        assert "Forwarding Statistics" in stats
        assert "Status                 : DELIVERED" in stats
        assert "Initial Hop Limit      : 64" in stats
        assert "Final Hop Limit        : 61" in stats
        assert "Routers Traversed      : 3 (R1, R2, R3)" in stats
        assert "2001:db8:1::10" in stats
        assert "2001:db8:4::20" in stats

    def test_format_header_view(self):
        """Test structured packet header visual view."""
        pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Header View Test")
        view = NetworkVisualizer.format_header_view(pkt)

        assert "IPv6 PACKET HEADER" in view
        assert "Version              : 6" in view
        assert "Traffic Class        : 0" in view
        assert "Flow Label           : 0" in view
        assert "Payload Length       : 16 bytes" in view
        assert "Next Header          : UDP (17)" in view
        assert "Hop Limit            : 64" in view
        assert "Source Address:\n2001:db8:1::10" in view
        assert "Destination Address:\n2001:db8:4::20" in view
        assert "Payload Content:\nHeader View Test" in view
