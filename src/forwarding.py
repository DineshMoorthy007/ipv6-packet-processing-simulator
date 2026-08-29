"""
IPv6 Packet Forwarding Simulation Module - IPv6 Packet Processing Simulator (Phase 4)

This module implements the end-to-end hop-by-hop packet forwarding engine,
Hop Limit checks and decrements, route lookup with Longest Prefix Match (LPM),
event logging, and delivery/drop handling.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from src.ipv6_address import analyze_ipv6
from src.ipv6_packet import IPv6Packet
from src.network import Host, NetworkTopology
from src.router import Router


class ForwardingStatus(str, Enum):
    """Enumeration of packet forwarding outcomes."""

    DELIVERED = "DELIVERED"
    DROPPED_HOP_LIMIT = "DROPPED_HOP_LIMIT"
    DROPPED_NO_ROUTE = "DROPPED_NO_ROUTE"
    DROPPED_INVALID = "DROPPED_INVALID"
    DROPPED_LOOP = "DROPPED_LOOP"


@dataclass
class ForwardingStep:
    """Represents an individual event/step in the forwarding lifecycle."""

    step_number: int
    node_name: str
    node_type: str
    action: str
    message: str
    hop_limit_before: int
    hop_limit_after: int
    details: Dict[str, Any] = field(default_factory=dict)


class ForwardingResult:
    """
    Structured container holding the complete outcome and event trace
    of an IPv6 packet forwarding simulation.
    """

    def __init__(
        self,
        status: ForwardingStatus,
        status_message: str,
        source_ip: str,
        destination_ip: str,
        initial_hop_limit: int,
        final_hop_limit: int,
        packet: IPv6Packet,
        path: List[str],
        routers_traversed: List[str],
        steps: List[ForwardingStep],
        log: List[str],
        source_host: Optional[str] = None,
        destination_host: Optional[str] = None,
    ):
        self.status: ForwardingStatus = status
        self.status_message: str = status_message
        self.source_ip: str = source_ip
        self.destination_ip: str = destination_ip
        self.initial_hop_limit: int = initial_hop_limit
        self.final_hop_limit: int = final_hop_limit
        self.packet: IPv6Packet = packet
        self.path: List[str] = path
        self.routers_traversed: List[str] = routers_traversed
        self.num_router_hops: int = len(routers_traversed)
        self.steps: List[ForwardingStep] = steps
        self.log: List[str] = log
        self.source_host: Optional[str] = source_host
        self.destination_host: Optional[str] = destination_host

    def to_dict(self) -> Dict[str, Any]:
        """Serialize forwarding result to dictionary."""
        return {
            "status": self.status.value if isinstance(self.status, ForwardingStatus) else str(self.status),
            "status_message": self.status_message,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "source_host": self.source_host,
            "destination_host": self.destination_host,
            "path": self.path,
            "routers_traversed": self.routers_traversed,
            "num_router_hops": self.num_router_hops,
            "initial_hop_limit": self.initial_hop_limit,
            "final_hop_limit": self.final_hop_limit,
            "log": self.log,
            "packet": self.packet.to_dict(),
        }

    def format_report(self) -> str:
        """
        Generate a comprehensive textual forwarding report.

        Returns
        -------
        str
            Formatted visual report.
        """
        lines = [
            "=" * 60,
            "             IPv6 PACKET FORWARDING SIMULATION",
            "=" * 60,
            "",
            "Packet Information:",
            "------------------------------------------------------------",
            f"Source Address      : {self.packet.source_address}" + (f" ({self.source_host})" if self.source_host else ""),
            f"Destination Address : {self.packet.destination_address}" + (f" ({self.destination_host})" if self.destination_host else ""),
            f"Payload             : {self.packet.payload if self.packet.payload else '<Empty>'}",
            f"Payload Length      : {self.packet.payload_length} bytes",
            f"Next Header         : {self.packet.next_header_name} ({self.packet.next_header})",
            f"Initial Hop Limit   : {self.initial_hop_limit}",
            "",
            "Forwarding Path:",
            "------------------------------------------------------------",
        ]

        # Draw path
        if self.path:
            for i, node in enumerate(self.path):
                lines.append(f"  {node}")
                if i < len(self.path) - 1:
                    lines.append("    |")
                    lines.append("    v")
        else:
            lines.append("  <No path traversed>")

        lines.extend([
            "",
            "Forwarding Result:",
            "------------------------------------------------------------",
            f"Status              : {self.status.value if isinstance(self.status, ForwardingStatus) else self.status}",
            f"Reason / Details    : {self.status_message}",
            f"Initial Hop Limit   : {self.initial_hop_limit}",
            f"Final Hop Limit     : {self.final_hop_limit}",
            f"Routers Traversed   : {self.num_router_hops} ({', '.join(self.routers_traversed) if self.routers_traversed else 'None'})",
            "",
            "=" * 60,
            "                 DETAILED FORWARDING EVENT LOG",
            "=" * 60,
        ])

        for entry in self.log:
            lines.append(entry)

        lines.append("=" * 60)
        return "\n".join(lines)


class PacketForwarder:
    """Engine executing hop-by-hop packet forwarding through a NetworkTopology."""

    @classmethod
    def forward(
        cls,
        packet: IPv6Packet,
        topology: NetworkTopology,
        source_host_name: Optional[str] = None,
    ) -> ForwardingResult:
        """
        Simulate the end-to-end traversal of an IPv6 packet across routers.

        Parameters
        ----------
        packet : IPv6Packet
            The simulated IPv6 packet to forward.
        topology : NetworkTopology
            The network topology containing hosts, routers, and links.
        source_host_name : Optional[str], optional
            Optional explicit source host name, by default None

        Returns
        -------
        ForwardingResult
            Structured report containing path, logs, and outcome.
        """
        dest_ip_str = packet.destination_address
        src_ip_str = packet.source_address
        dest_ip_obj = ipaddress.IPv6Address(dest_ip_str)

        initial_hop_limit = packet.hop_limit
        path: List[str] = []
        routers_traversed: List[str] = []
        steps: List[ForwardingStep] = []
        log_entries: List[str] = []
        step_counter = 1

        def add_log(msg: str):
            nonlocal step_counter
            entry = f"[{step_counter}] {msg}"
            log_entries.append(entry)
            step_counter += 1

        # 1. Identify Source Host
        src_host: Optional[Host] = None
        if source_host_name:
            src_host = topology.get_host(source_host_name)
        if not src_host:
            # Search by IP
            for h in topology.hosts.values():
                if h.ipv6_address == src_ip_str:
                    src_host = h
                    break

        src_name = src_host.name if src_host else f"Source ({src_ip_str})"
        path.append(src_name)

        # 2. Identify Destination Host in topology if present
        dst_host: Optional[Host] = None
        for h in topology.hosts.values():
            if h.ipv6_address == dest_ip_str:
                dst_host = h
                break
        dst_name = dst_host.name if dst_host else f"Destination ({dest_ip_str})"

        # Log packet creation
        add_log(
            f"Packet created at {src_name}\n"
            f"    Source      : {src_ip_str}\n"
            f"    Destination : {dest_ip_str}\n"
            f"    Hop Limit   : {packet.hop_limit}"
        )

        # 3. Check if destination is on the source host's local subnet
        if src_host:
            src_net = ipaddress.IPv6Network(src_host.network, strict=False)
            if dest_ip_obj in src_net:
                # Direct local delivery on the same subnet (no routers needed)
                path.append(dst_name)
                add_log(
                    f"Destination {dest_ip_str} is on the local subnet ({src_host.network}).\n"
                    f"    Direct local delivery to {dst_name} without router hops."
                )
                add_log("PACKET DELIVERED SUCCESSFULLY")
                return ForwardingResult(
                    status=ForwardingStatus.DELIVERED,
                    status_message="Direct local delivery on source subnet (0 router hops)",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=[],
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

        # 4. Determine initial gateway router from source host
        current_router: Optional[Router] = None
        if src_host and src_host.default_gateway:
            gw_ip = src_host.default_gateway
            # Find which router has this gateway IP on one of its interfaces
            for r in topology.routers.values():
                for intf in r.interfaces.values():
                    if intf.ip_address == gw_ip:
                        current_router = r
                        break
                if current_router:
                    break

        if not current_router:
            # Fallback: find router whose interface is on source host's subnet
            for r in topology.routers.values():
                for intf in r.interfaces.values():
                    intf_net = ipaddress.IPv6Network(intf.network, strict=False)
                    if ipaddress.IPv6Address(src_ip_str) in intf_net:
                        current_router = r
                        break
                if current_router:
                    break

        if not current_router:
            add_log(f"Error: Source host '{src_name}' has no reachable default gateway router.")
            add_log("PACKET DROPPED (Reason: No default gateway router reachable)")
            return ForwardingResult(
                status=ForwardingStatus.DROPPED_NO_ROUTE,
                status_message=f"No default gateway found for source '{src_name}'",
                source_ip=src_ip_str,
                destination_ip=dest_ip_str,
                initial_hop_limit=initial_hop_limit,
                final_hop_limit=packet.hop_limit,
                packet=packet,
                path=path,
                routers_traversed=[],
                steps=steps,
                log=log_entries,
                source_host=src_name,
                destination_host=dst_name,
            )

        # 5. Router Hop-by-Hop Traversal Loop
        max_hops = 256
        hop_count = 0

        while current_router:
            hop_count += 1
            if hop_count > max_hops:
                add_log("PACKET DROPPED (Reason: Routing loop detected / Max hops exceeded)")
                return ForwardingResult(
                    status=ForwardingStatus.DROPPED_LOOP,
                    status_message="Routing loop detected (exceeded 256 hops)",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=routers_traversed,
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

            r_name = current_router.name
            path.append(r_name)
            routers_traversed.append(r_name)

            hl_in = packet.hop_limit
            add_log(f"Packet received by {r_name}\n    Hop Limit   : {hl_in}")

            # Step 1: Check if destination is directly connected on this router
            is_directly_connected = False
            egress_interface = None
            for intf_name, intf in current_router.interfaces.items():
                intf_net = ipaddress.IPv6Network(intf.network, strict=False)
                if dest_ip_obj in intf_net:
                    is_directly_connected = True
                    egress_interface = intf_name
                    break

            if is_directly_connected:
                # Destination network is directly connected to current router
                # Check Hop Limit before final delivery
                if packet.hop_limit <= 1:
                    add_log(
                        f"Hop Limit expired on {r_name} (Hop Limit = {packet.hop_limit} <= 1).\n"
                        f"    PACKET DROPPED\n"
                        f"    Reason: Hop Limit expired"
                    )
                    return ForwardingResult(
                        status=ForwardingStatus.DROPPED_HOP_LIMIT,
                        status_message="Hop Limit expired at router",
                        source_ip=src_ip_str,
                        destination_ip=dest_ip_str,
                        initial_hop_limit=initial_hop_limit,
                        final_hop_limit=packet.hop_limit,
                        packet=packet,
                        path=path,
                        routers_traversed=routers_traversed,
                        steps=steps,
                        log=log_entries,
                        source_host=src_name,
                        destination_host=dst_name,
                    )

                # Decrement Hop Limit for the final router hop
                old_hl = packet.hop_limit
                packet.hop_limit -= 1
                new_hl = packet.hop_limit

                add_log(
                    f"Destination network is directly connected on {r_name} ({egress_interface})\n"
                    f"    Hop Limit   : {old_hl} -> {new_hl}"
                )
                path.append(dst_name)
                add_log(f"Packet delivered to {dst_name}")
                add_log("PACKET DELIVERED SUCCESSFULLY")

                return ForwardingResult(
                    status=ForwardingStatus.DELIVERED,
                    status_message="Packet delivered successfully",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=routers_traversed,
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

            # Step 2: Not directly connected -> Must forward. Check Hop Limit!
            if packet.hop_limit <= 1:
                add_log(
                    f"Hop Limit expired on {r_name} (Hop Limit = {packet.hop_limit} <= 1).\n"
                    f"    PACKET DROPPED\n"
                    f"    Reason: Hop Limit expired"
                )
                return ForwardingResult(
                    status=ForwardingStatus.DROPPED_HOP_LIMIT,
                    status_message="Hop Limit expired at router",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=routers_traversed,
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

            # Decrement Hop Limit
            old_hl = packet.hop_limit
            packet.hop_limit -= 1
            new_hl = packet.hop_limit

            # Step 3: Route Lookup & Longest Prefix Match
            add_log(f"{r_name} performing route lookup\n    Destination : {dest_ip_str}")
            lookup_result = current_router.lookup_route(dest_ip_str)

            if lookup_result["status"] != "SUCCESS" or not lookup_result["selected_route"]:
                add_log(
                    f"No route to destination {dest_ip_str} found on {r_name}.\n"
                    f"    PACKET DROPPED\n"
                    f"    Reason: No matching route found"
                )
                return ForwardingResult(
                    status=ForwardingStatus.DROPPED_NO_ROUTE,
                    status_message=f"No matching route found in routing table of {r_name}",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=routers_traversed,
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

            selected_prefix = lookup_result["selected_prefix"]
            next_hop_ip = lookup_result["next_hop"]
            out_interface = lookup_result["interface"]

            add_log(
                f"{r_name} selected route (Longest Prefix Match)\n"
                f"    Prefix      : {selected_prefix}\n"
                f"    Next Hop    : {next_hop_ip}\n"
                f"    Interface   : {out_interface}"
            )

            add_log(
                f"{r_name} forwarding packet via {out_interface}\n"
                f"    Hop Limit   : {old_hl} -> {new_hl}"
            )

            # Step 4: Locate next router in topology by next_hop IP
            next_router: Optional[Router] = None
            for r in topology.routers.values():
                for intf in r.interfaces.values():
                    if intf.ip_address == next_hop_ip:
                        next_router = r
                        break
                if next_router:
                    break

            if not next_router:
                add_log(
                    f"Next hop router with IP '{next_hop_ip}' not found in topology.\n"
                    f"    PACKET DROPPED\n"
                    f"    Reason: Next hop unreachable"
                )
                return ForwardingResult(
                    status=ForwardingStatus.DROPPED_NO_ROUTE,
                    status_message=f"Next hop router '{next_hop_ip}' unreachable",
                    source_ip=src_ip_str,
                    destination_ip=dest_ip_str,
                    initial_hop_limit=initial_hop_limit,
                    final_hop_limit=packet.hop_limit,
                    packet=packet,
                    path=path,
                    routers_traversed=routers_traversed,
                    steps=steps,
                    log=log_entries,
                    source_host=src_name,
                    destination_host=dst_name,
                )

            current_router = next_router

        # Fallback return
        return ForwardingResult(
            status=ForwardingStatus.DROPPED_NO_ROUTE,
            status_message="Forwarding terminated without delivery",
            source_ip=src_ip_str,
            destination_ip=dest_ip_str,
            initial_hop_limit=initial_hop_limit,
            final_hop_limit=packet.hop_limit,
            packet=packet,
            path=path,
            routers_traversed=routers_traversed,
            steps=steps,
            log=log_entries,
            source_host=src_name,
            destination_host=dst_name,
        )


def forward_packet(
    packet: IPv6Packet,
    topology: NetworkTopology,
    source_host_name: Optional[str] = None,
) -> ForwardingResult:
    """Convenience helper to forward a packet through a network topology."""
    return PacketForwarder.forward(
        packet=packet,
        topology=topology,
        source_host_name=source_host_name,
    )
