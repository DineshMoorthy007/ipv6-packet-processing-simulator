"""
Simulated IPv6 Network Topology Module - IPv6 Packet Processing Simulator (Phase 3 & 6)

This module defines `NetworkTopology` to manage devices, links, and sample
multi-hop topologies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.host import Host, Link
from src.router import Router


class NetworkTopology:
    """
    Manages hosts, routers, links, and topology rendering.
    """

    def __init__(self, name: str = "Simulated IPv6 Network"):
        self.name: str = name
        self.hosts: Dict[str, Host] = {}
        self.routers: Dict[str, Router] = {}
        self.links: List[Link] = []

    def add_host(
        self,
        name: str,
        ipv6_address_cidr: str,
        default_gateway: Optional[str] = None,
        interface: str = "eth0",
    ) -> Host:
        """Add an end-host to the topology."""
        host = Host(
            name=name,
            ipv6_address_cidr=ipv6_address_cidr,
            default_gateway=default_gateway,
            interface=interface,
        )
        self.hosts[host.name] = host
        return host

    def add_router(self, router: Router) -> Router:
        """Add a router to the topology."""
        self.routers[router.name] = router
        return router

    def add_link(
        self,
        node_a: str,
        interface_a: str,
        node_b: str,
        interface_b: str,
        network: str,
    ) -> Link:
        """Create a link between two devices."""
        link = Link(
            node_a=node_a,
            interface_a=interface_a,
            node_b=node_b,
            interface_b=interface_b,
            network=network,
        )
        self.links.append(link)
        return link

    def get_router(self, name: str) -> Optional[Router]:
        """Get a router by name."""
        return self.routers.get(name.strip())

    def get_host(self, name: str) -> Optional[Host]:
        """Get a host by name."""
        return self.hosts.get(name.strip())

    def display_topology(self) -> str:
        """
        Render a clean ASCII diagram and overview of the network topology.

        Returns
        -------
        str
            Formatted textual topology diagram.
        """
        lines = [
            "=" * 65,
            f"           NETWORK TOPOLOGY: {self.name.upper()}",
            "=" * 65,
            "",
            "Topology Diagram:",
            "-----------------------------------------------------------------",
            "  [Host A] (2001:db8:1::10/64)  -- GW: 2001:db8:1::1",
            "     |",
            "   (Subnet: 2001:db8:1::/64)",
            "     |",
            "  [Router R1]",
            "     +-- eth0: 2001:db8:1::1/64",
            "     +-- eth1: 2001:db8:2::1/64",
            "     |",
            "   (Subnet: 2001:db8:2::/64)",
            "     |",
            "  [Router R2]",
            "     +-- eth0: 2001:db8:2::2/64",
            "     +-- eth1: 2001:db8:3::1/64",
            "     |",
            "   (Subnet: 2001:db8:3::/64)",
            "     |",
            "  [Router R3]",
            "     +-- eth0: 2001:db8:3::2/64",
            "     +-- eth1: 2001:db8:4::1/64",
            "     |",
            "   (Subnet: 2001:db8:4::/64)",
            "     |",
            "  [Host B] (2001:db8:4::20/64)  -- GW: 2001:db8:4::1",
            "-----------------------------------------------------------------",
            "",
            "Configured Devices:",
            f"  Routers : {', '.join(self.routers.keys())}",
            f"  Hosts   : {', '.join(self.hosts.keys())}",
            f"  Links   : {len(self.links)} active subnets",
            "=" * 65,
        ]
        return "\n".join(lines)


def build_sample_topology() -> NetworkTopology:
    """
    Construct and return the reference 3-router IPv6 network topology
    with configured interfaces and static routes.

    Returns
    -------
    NetworkTopology
        Configured sample topology.
    """
    topo = NetworkTopology("Sample 3-Router Linear Network")

    # 1. Create Hosts
    topo.add_host(
        name="Host A",
        ipv6_address_cidr="2001:db8:1::10/64",
        default_gateway="2001:db8:1::1",
        interface="eth0",
    )
    topo.add_host(
        name="Host B",
        ipv6_address_cidr="2001:db8:4::20/64",
        default_gateway="2001:db8:4::1",
        interface="eth0",
    )

    # 2. Create Routers
    r1 = Router(name="R1", router_id="r1")
    r2 = Router(name="R2", router_id="r2")
    r3 = Router(name="R3", router_id="r3")

    # Configure R1 interfaces
    r1.add_interface("eth0", "2001:db8:1::1/64")
    r1.add_interface("eth1", "2001:db8:2::1/64")

    # Configure R2 interfaces
    r2.add_interface("eth0", "2001:db8:2::2/64")
    r2.add_interface("eth1", "2001:db8:3::1/64")

    # Configure R3 interfaces
    r3.add_interface("eth0", "2001:db8:3::2/64")
    r3.add_interface("eth1", "2001:db8:4::1/64")

    # 3. Configure Static Routes
    # R1 knows about Subnet 3 & Subnet 4 via R2 (2001:db8:2::2)
    r1.add_static_route("2001:db8:3::/64", next_hop="2001:db8:2::2", interface="eth1")
    r1.add_static_route("2001:db8:4::/64", next_hop="2001:db8:2::2", interface="eth1")

    # R2 knows about Subnet 1 via R1 (2001:db8:2::1) and Subnet 4 via R3 (2001:db8:3::2)
    r2.add_static_route("2001:db8:1::/64", next_hop="2001:db8:2::1", interface="eth0")
    r2.add_static_route("2001:db8:4::/64", next_hop="2001:db8:3::2", interface="eth1")

    # R3 knows about Subnet 1 & Subnet 2 via R2 (2001:db8:3::1)
    r3.add_static_route("2001:db8:1::/64", next_hop="2001:db8:3::1", interface="eth0")
    r3.add_static_route("2001:db8:2::/64", next_hop="2001:db8:3::1", interface="eth0")

    # Register Routers in Topology
    topo.add_router(r1)
    topo.add_router(r2)
    topo.add_router(r3)

    # 4. Create Links
    topo.add_link("Host A", "eth0", "R1", "eth0", "2001:db8:1::/64")
    topo.add_link("R1", "eth1", "R2", "eth0", "2001:db8:2::/64")
    topo.add_link("R2", "eth1", "R3", "eth0", "2001:db8:3::/64")
    topo.add_link("R3", "eth1", "Host B", "eth0", "2001:db8:4::/64")

    return topo
