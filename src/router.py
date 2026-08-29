"""
IPv6 Router & Interface Management Module - IPv6 Packet Processing Simulator (Phase 3)

This module implements the `Router` and `RouterInterface` classes, supporting
IPv6 interface assignments, automated connected route generation, static route
configuration, and route lookup with Longest Prefix Match (LPM).
"""

from __future__ import annotations

import ipaddress
from typing import Any, Dict, List, Optional
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6
from src.routing_table import Route, RoutingTable


class RouterInterface:
    """
    Representation of a network interface configured on an IPv6 router.

    Attributes
    ----------
    name : str
        Interface identifier (e.g. 'eth0', 'eth1').
    ipv6_interface : ipaddress.IPv6Interface
        The parsed IPv6 interface object containing IP and subnet prefix.
    ip_address : str
        Configured IPv6 address (compressed).
    network : str
        Connected IPv6 network prefix in CIDR notation (e.g. '2001:db8:1::/64').
    prefix_length : int
        Subnet prefix length in bits.
    is_up : bool
        Operational status of the interface (default: True).
    """

    def __init__(self, name: str, ipv6_address_cidr: str, is_up: bool = True):
        if not name or not isinstance(name, str):
            raise ValueError("Interface name must be a non-empty string.")
        self.name: str = name.strip()

        if not ipv6_address_cidr or not isinstance(ipv6_address_cidr, str):
            raise ValueError("Interface IPv6 address/CIDR must be a non-empty string.")

        cleaned_cidr = ipv6_address_cidr.strip()
        # If user did not provide prefix length, default to /64
        if "/" not in cleaned_cidr:
            cleaned_cidr = f"{cleaned_cidr}/64"

        try:
            self.ipv6_interface: ipaddress.IPv6Interface = ipaddress.IPv6Interface(cleaned_cidr)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as err:
            raise ValueError(f"Invalid IPv6 interface configuration '{ipv6_address_cidr}': {err}")

        self.ip_address: str = self.ipv6_interface.ip.compressed
        self.network: str = self.ipv6_interface.network.compressed
        self.prefix_length: int = self.ipv6_interface.network.prefixlen
        self.is_up: bool = is_up

    def to_dict(self) -> Dict[str, Any]:
        """Convert interface properties to dictionary."""
        return {
            "name": self.name,
            "ip_address": self.ip_address,
            "network": self.network,
            "prefix_length": self.prefix_length,
            "is_up": self.is_up,
        }

    def __repr__(self) -> str:
        return f"RouterInterface(name='{self.name}', ip='{self.ip_address}/{self.prefix_length}', is_up={self.is_up})"


class Router:
    """
    Representation of an IPv6 Router node.

    Attributes
    ----------
    name : str
        Router name (e.g. 'R1', 'CoreRouter').
    router_id : str
        Unique identifier for the router.
    interfaces : Dict[str, RouterInterface]
        Dictionary of configured interfaces keyed by interface name.
    routing_table : RoutingTable
        The router's active IPv6 routing table.
    """

    def __init__(self, name: str, router_id: Optional[str] = None):
        if not name or not isinstance(name, str):
            raise ValueError("Router name must be a non-empty string.")
        self.name: str = name.strip()
        self.router_id: str = str(router_id).strip() if router_id else self.name.lower()
        self.interfaces: Dict[str, RouterInterface] = {}
        self.routing_table: RoutingTable = RoutingTable()

    def add_interface(self, interface_name: str, ipv6_cidr: str, is_up: bool = True) -> RouterInterface:
        """
        Add a network interface to the router and automatically register
        a directly connected route in the routing table.

        Parameters
        ----------
        interface_name : str
            Interface name (e.g. 'eth0').
        ipv6_cidr : str
            IPv6 address with CIDR prefix (e.g. '2001:db8:1::1/64').
        is_up : bool, optional
            Interface state, by default True

        Returns
        -------
        RouterInterface
            The configured interface object.
        """
        interface = RouterInterface(name=interface_name, ipv6_address_cidr=ipv6_cidr, is_up=is_up)
        self.interfaces[interface.name] = interface

        # Automatically add connected route
        if interface.is_up:
            self.routing_table.add_route(
                destination_prefix=interface.network,
                next_hop="Direct",
                interface=interface.name,
                route_type="Connected",
                metric=0,
            )

        return interface

    def remove_interface(self, interface_name: str) -> bool:
        """
        Remove an interface from the router and clear its associated routes.

        Parameters
        ----------
        interface_name : str
            Interface name to remove.

        Returns
        -------
        bool
            True if removed, False if interface did not exist.
        """
        clean_name = interface_name.strip()
        if clean_name in self.interfaces:
            del self.interfaces[clean_name]
            self.routing_table.remove_interface_routes(clean_name)
            return True
        return False

    def add_static_route(
        self,
        destination_prefix: str,
        next_hop: str,
        interface: str,
        metric: int = 1,
    ) -> Route:
        """
        Add a static IPv6 route to the routing table.

        Parameters
        ----------
        destination_prefix : str
            Destination subnet (e.g. '2001:db8:4::/64').
        next_hop : str
            Next hop router IPv6 address (e.g. '2001:db8:2::2').
        interface : str
            Outgoing interface (e.g. 'eth1').
        metric : int, optional
            Administrative metric, by default 1

        Returns
        -------
        Route
            The added static route.
        """
        return self.routing_table.add_route(
            destination_prefix=destination_prefix,
            next_hop=next_hop,
            interface=interface,
            route_type="Static",
            metric=metric,
        )

    def lookup_route(self, destination_ip: str) -> Dict[str, Any]:
        """
        Perform a routing table lookup for a destination IPv6 address
        using Longest Prefix Match (LPM).

        Parameters
        ----------
        destination_ip : str
            The destination IPv6 address (e.g. '2001:db8:4::20').

        Returns
        -------
        Dict[str, Any]
            Detailed route lookup report.
        """
        # Validate destination address
        is_valid, err_msg = IPv6AddressAnalyzer.validate(destination_ip)
        if not is_valid:
            return {
                "router": self.name,
                "destination": destination_ip,
                "is_valid": False,
                "error_message": err_msg,
                "matching_routes": [],
                "matching_prefixes": [],
                "selected_route": None,
                "selected_prefix": None,
                "next_hop": None,
                "interface": None,
                "route_type": None,
                "status": "INVALID_DESTINATION",
            }

        # Normalize address string
        dest_res = analyze_ipv6(destination_ip)
        norm_dest = dest_res.compressed or destination_ip.strip()

        matching = self.routing_table.get_matching_routes(norm_dest)
        best = matching[0] if matching else None

        return {
            "router": self.name,
            "destination": norm_dest,
            "is_valid": True,
            "error_message": None,
            "matching_routes": [r.to_dict() for r in matching],
            "matching_prefixes": [r.destination_prefix for r in matching],
            "selected_route": best.to_dict() if best else None,
            "selected_prefix": best.destination_prefix if best else None,
            "next_hop": best.next_hop if best else None,
            "interface": best.interface if best else None,
            "route_type": best.route_type if best else None,
            "status": "SUCCESS" if best else "NO_ROUTE",
        }

    def format_lookup_result(self, result: Dict[str, Any]) -> str:
        """
        Format a route lookup dictionary into a clean textual output.

        Parameters
        ----------
        result : Dict[str, Any]
            The route lookup result from `lookup_route()`.

        Returns
        -------
        str
            Formatted textual output matching project specification.
        """
        lines = [
            "ROUTE LOOKUP",
            "=" * 40,
            "",
            "Router:",
            f"{result['router']}",
            "",
            "Destination:",
            f"{result['destination']}",
            "",
        ]

        if not result["is_valid"]:
            lines.append("Status:")
            lines.append("Invalid Destination Address")
            lines.append(f"Error: {result['error_message']}")
            lines.append("=" * 40)
            return "\n".join(lines)

        if result["status"] == "NO_ROUTE":
            lines.append("Matching Prefix:")
            lines.append("None")
            lines.append("")
            lines.append("Status:")
            lines.append("No Route to Host")
            lines.append("=" * 40)
            return "\n".join(lines)

        # When matching routes exist
        if len(result["matching_prefixes"]) > 1:
            lines.append("Matching Routes (LPM Candidates):")
            for prefix in result["matching_prefixes"]:
                lines.append(f"  - {prefix}")
            lines.append("")

        lines.append("Matching Prefix:")
        lines.append(f"{result['selected_prefix']}")
        lines.append("")
        lines.append("Selected Route:")
        lines.append(f"{result['selected_prefix']}")
        lines.append("")
        lines.append("Next Hop:")
        lines.append(f"{result['next_hop']}")
        lines.append("")
        lines.append("Interface:")
        lines.append(f"{result['interface']}")
        lines.append("")
        lines.append("Route Type:")
        lines.append(f"{result['route_type']}")
        lines.append("=" * 40)

        return "\n".join(lines)

    def display_router_info(self) -> str:
        """
        Format the router's interface configuration and routing table for display.

        Returns
        -------
        str
            Formatted summary of router state.
        """
        lines = [
            f"Router {self.name}",
            "=" * 50,
            "Interfaces",
            "-" * 50,
        ]

        if not self.interfaces:
            lines.append("No interfaces configured.")
        else:
            for name, intf in self.interfaces.items():
                status = "UP" if intf.is_up else "DOWN"
                lines.append(f"{name:<6} : {intf.ip_address}/{intf.prefix_length:<3} [{status}]")

        lines.append("")
        lines.append("Routing Table")
        lines.append("-" * 50)
        lines.append(self.routing_table.display_table())
        lines.append("=" * 50)

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Router(name='{self.name}', interfaces={len(self.interfaces)}, routes={len(self.routing_table)})"
