"""
Network Visualization & Simulation Dashboard Module - IPv6 Packet Processing Simulator (Phase 5)

This module provides rich visual formatting, device inspectors, step-by-step
packet movement snapshots, processing timelines, statistics dashboards, and
structured IPv6 header views.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.forwarding import ForwardingResult, ForwardingStatus
from src.ipv6_packet import IPv6Packet
from src.network import Host, NetworkTopology
from src.router import Router


class NetworkVisualizer:
    """Utility class providing visual formatting and simulation dashboards."""

    @classmethod
    def format_topology_graph(
        cls,
        topology: NetworkTopology,
        active_path: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a visual ASCII network diagram of the topology, highlighting active path.

        Parameters
        ----------
        topology : NetworkTopology
            The network topology.
        active_path : Optional[List[str]], optional
            List of node names currently participating in forwarding path.

        Returns
        -------
        str
            Formatted diagram string.
        """
        path_set = set(active_path) if active_path else set()

        def node_tag(name: str) -> str:
            return f"[* {name} *]" if name in path_set else f"[ {name} ]"

        lines = [
            "=" * 70,
            f"          TOPOLOGY VISUALIZATION: {topology.name.upper()}",
            "=" * 70,
            "",
            "Network Architecture Diagram:",
            "----------------------------------------------------------------------",
            f"  +-----------+         +--------+         +--------+         +--------+         +-----------+",
            f"  |  {node_tag('Host A'):<9} |---------|  {node_tag('R1'):<6} |---------|  {node_tag('R2'):<6} |---------|  {node_tag('R3'):<6} |---------|  {node_tag('Host B'):<9} |",
            f"  +-----------+         +--------+         +--------+         +--------+         +-----------+",
            " 2001:db8:1::/64     2001:db8:2::/64    2001:db8:3::/64    2001:db8:4::/64",
            "----------------------------------------------------------------------",
        ]

        if active_path:
            lines.append("")
            lines.append("Active Forwarding Path:")
            lines.append("  " + " -> ".join(f"[{node}]" for node in active_path))

        lines.extend([
            "",
            "Device Inventory:",
            f"  Hosts   : {', '.join(topology.hosts.keys())}",
            f"  Routers : {', '.join(topology.routers.keys())}",
            f"  Subnets : {len(topology.links)} configured links",
            "=" * 70,
        ])
        return "\n".join(lines)

    @classmethod
    def format_device_details(cls, device_name: str, topology: NetworkTopology) -> str:
        """
        Generate a detailed device information card for a Host or Router.

        Parameters
        ----------
        device_name : str
            Name of host or router.
        topology : NetworkTopology
            The network topology.

        Returns
        -------
        str
            Formatted device card.
        """
        clean_name = device_name.strip()
        host = topology.get_host(clean_name)
        if host:
            lines = [
                "HOST INFORMATION",
                "=" * 45,
                f"Name         : {host.name}",
                f"IPv6 Address : {host.ipv6_address}/{host.prefix_length}",
                f"Subnet       : {host.network}",
                f"Gateway      : {host.default_gateway if host.default_gateway else 'None'}",
                f"Interface    : {host.interface}",
                "=" * 45,
            ]
            return "\n".join(lines)

        router = topology.get_router(clean_name)
        if router:
            lines = [
                "ROUTER INFORMATION",
                "=" * 60,
                f"Router Name : {router.name}",
                f"Router ID   : {router.router_id}",
                "",
                "Configured Interfaces:",
                "-" * 60,
            ]
            for intf_name, intf in router.interfaces.items():
                status = "UP" if intf.is_up else "DOWN"
                lines.append(f"  {intf_name:<6} -> {intf.ip_address}/{intf.prefix_length:<3} (Subnet: {intf.network}) [{status}]")

            lines.extend([
                "",
                "Active Routing Table:",
                "-" * 60,
                router.routing_table.display_table(),
                "=" * 60,
            ])
            return "\n".join(lines)

        return f"Error: Device '{device_name}' not found in topology."

    @classmethod
    def format_packet_movement_steps(cls, result: ForwardingResult) -> List[str]:
        """
        Generate step-by-step visual snapshots of packet movement across nodes.

        Parameters
        ----------
        result : ForwardingResult
            The forwarding result from Phase 4.

        Returns
        -------
        List[str]
            List of formatted snapshot strings.
        """
        snapshots = []
        path = result.path
        if not path:
            return ["No movement path available."]

        # Calculate current Hop Limit at each hop
        current_hl = result.initial_hop_limit

        for step_idx, node in enumerate(path):
            # Highlight current location in full path
            highlighted_nodes = []
            for n in path:
                if n == node:
                    highlighted_nodes.append(f">>> [{n}] <<<")
                else:
                    highlighted_nodes.append(f"[{n}]")

            path_display = " -> ".join(highlighted_nodes)

            # Determine hop limit at this step
            if step_idx == 0:
                step_hl = result.initial_hop_limit
            elif step_idx == len(path) - 1 and result.status == ForwardingStatus.DELIVERED:
                step_hl = result.final_hop_limit
            else:
                step_hl = max(0, result.initial_hop_limit - step_idx)

            lines = [
                f"--- Step {step_idx + 1} of {len(path)} ---",
                f"Path Flow        : {path_display}",
                f"Current Location : {node}",
                f"Hop Limit        : {step_hl}",
            ]

            if step_idx == len(path) - 1:
                if result.status == ForwardingStatus.DELIVERED:
                    lines.append("Status           : PACKET DELIVERED SUCCESSFULLY")
                else:
                    lines.append(f"Status           : PACKET DROPPED ({result.status_message})")

            snapshots.append("\n".join(lines))

        return snapshots

    @classmethod
    def format_forwarding_timeline(cls, result: ForwardingResult) -> str:
        """
        Generate a clean, structured timeline from forwarding events.

        Parameters
        ----------
        result : ForwardingResult
            The forwarding result.

        Returns
        -------
        str
            Formatted timeline string.
        """
        lines = [
            "PACKET PROCESSING TIMELINE",
            "=" * 60,
        ]

        timeline_items = []
        for entry in result.log:
            clean_entry = entry.strip()
            # Remove the [number] prefix if present
            if clean_entry.startswith("[") and "]" in clean_entry:
                clean_entry = clean_entry.split("]", 1)[1].strip()

            entry_lines = [l.strip() for l in clean_entry.split("\n") if l.strip()]
            if not entry_lines:
                continue

            first_line = entry_lines[0]
            is_drop = any("PACKET DROPPED" in l or "expired" in l.lower() or "no route" in l.lower() for l in entry_lines)
            is_delivered = any("PACKET DELIVERED" in l for l in entry_lines)

            if is_drop:
                # If there's a reason line or PACKET DROPPED line, combine for clarity
                drop_detail = next((l for l in entry_lines if "Reason:" in l), first_line)
                timeline_items.append(f"[X] {first_line} -> PACKET DROPPED ({drop_detail})")
            elif is_delivered:
                timeline_items.append(f"[OK] {first_line}")
            else:
                timeline_items.append(f"[OK] {first_line}")

        if not timeline_items:
            return "No timeline events available."

        for i, item in enumerate(timeline_items):
            lines.append(f"  {item}")
            if i < len(timeline_items) - 1:
                lines.append("        |")
                lines.append("        v")

        lines.append("=" * 60)
        return "\n".join(lines)

    @classmethod
    def format_forwarding_stats(cls, result: ForwardingResult) -> str:
        """
        Generate a structured forwarding statistics summary.

        Parameters
        ----------
        result : ForwardingResult
            The forwarding result.

        Returns
        -------
        str
            Formatted statistics table.
        """
        lines = [
            "Forwarding Statistics",
            "-" * 45,
            f"Status                 : {result.status.value if isinstance(result.status, ForwardingStatus) else result.status}",
            f"Reason / Details       : {result.status_message}",
            f"Initial Hop Limit      : {result.initial_hop_limit}",
            f"Final Hop Limit        : {result.final_hop_limit}",
            f"Routers Traversed      : {result.num_router_hops} ({', '.join(result.routers_traversed) if result.routers_traversed else 'None'})",
            f"Total Event Steps      : {len(result.log)}",
            f"Source Address         : {result.source_ip}" + (f" ({result.source_host})" if result.source_host else ""),
            f"Destination Address    : {result.destination_ip}" + (f" ({result.destination_host})" if result.destination_host else ""),
            "-" * 45,
        ]
        return "\n".join(lines)

    @classmethod
    def format_header_view(cls, packet: IPv6Packet) -> str:
        """
        Format the IPv6 packet header in a clear, structured format.

        Parameters
        ----------
        packet : IPv6Packet
            The IPv6 packet.

        Returns
        -------
        str
            Formatted header visual view.
        """
        lines = [
            "=" * 50,
            "              IPv6 PACKET HEADER",
            "=" * 50,
            f"Version              : {packet.version}",
            f"Traffic Class        : {packet.traffic_class}",
            f"Flow Label           : {packet.flow_label}",
            f"Payload Length       : {packet.payload_length} bytes",
            f"Next Header          : {packet.next_header_name} ({packet.next_header})",
            f"Hop Limit            : {packet.hop_limit}",
            "",
            "Source Address:",
            f"{packet.source_address}",
            "",
            "Destination Address:",
            f"{packet.destination_address}",
            "=" * 50,
            "Payload Content:",
            f"{packet.payload if packet.payload else '<Empty Payload>'}",
            "=" * 50,
        ]
        return "\n".join(lines)

    @classmethod
    def get_topology_graph_data(
        cls,
        topology: NetworkTopology,
        active_path: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Export structured topology node and link graph data for GUI / Streamlit integration.

        Parameters
        ----------
        topology : NetworkTopology
            The network topology.
        active_path : Optional[List[str]], optional
            Current active forwarding path.

        Returns
        -------
        Dict[str, Any]
            Graph dictionary containing nodes, edges, subnets, and active path.
        """
        path_set = set(active_path) if active_path else set()

        nodes = []
        for host in topology.hosts.values():
            nodes.append({
                "id": host.name,
                "type": "host",
                "label": host.name,
                "ip": host.ipv6_address,
                "subnet": host.network,
                "gateway": host.default_gateway,
                "is_active": host.name in path_set,
            })

        for router in topology.routers.values():
            nodes.append({
                "id": router.name,
                "type": "router",
                "label": router.name,
                "interfaces": [intf.to_dict() for intf in router.interfaces.values()],
                "routes": router.routing_table.to_list(),
                "is_active": router.name in path_set,
            })

        edges = []
        for link in topology.links:
            edges.append({
                "source": link.node_a,
                "source_interface": link.interface_a,
                "target": link.node_b,
                "target_interface": link.interface_b,
                "network": link.network,
                "is_active": (link.node_a in path_set and link.node_b in path_set),
            })

        return {
            "name": topology.name,
            "nodes": nodes,
            "edges": edges,
            "active_path": active_path if active_path else [],
        }
