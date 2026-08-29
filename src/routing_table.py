"""
IPv6 Routing Table & Route Lookup Module - IPv6 Packet Processing Simulator (Phase 3)

This module implements the `Route` and `RoutingTable` classes, supporting
Connected and Static routes, route validation, and Longest Prefix Match (LPM).
"""

from __future__ import annotations

import ipaddress
from typing import Any, Dict, List, Optional, Union
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6


class Route:
    """
    Representation of an individual IPv6 Route entry in a routing table.

    Attributes
    ----------
    destination_prefix : str
        The destination network prefix in CIDR notation (e.g. '2001:db8:1::/64').
    destination_network : ipaddress.IPv6Network
        The parsed IPv6 network object.
    prefix_length : int
        The prefix length in bits (0-128).
    next_hop : str
        Next hop IPv6 address or 'Direct' for directly connected networks.
    interface : str
        The outgoing network interface name (e.g. 'eth0', 'eth1').
    route_type : str
        Type of route ('Connected', 'Static').
    metric : int
        Administrative distance / routing metric (default: 1).
    """

    def __init__(
        self,
        destination_prefix: str,
        next_hop: Optional[str],
        interface: str,
        route_type: str = "Static",
        metric: int = 1,
    ):
        # 1. Validate destination prefix
        if not destination_prefix or not isinstance(destination_prefix, str):
            raise ValueError("Destination prefix must be a non-empty string.")

        cleaned_prefix = destination_prefix.strip()
        try:
            self.destination_network: ipaddress.IPv6Network = ipaddress.IPv6Network(cleaned_prefix, strict=False)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as err:
            raise ValueError(f"Invalid IPv6 destination prefix '{destination_prefix}': {err}")

        self.destination_prefix: str = self.destination_network.compressed
        self.prefix_length: int = self.destination_network.prefixlen

        # 2. Validate interface
        if not interface or not isinstance(interface, str):
            raise ValueError("Interface name must be a non-empty string.")
        self.interface: str = interface.strip()

        # 3. Validate route type
        cleaned_type = str(route_type).strip().capitalize() if route_type else "Static"
        if cleaned_type not in ("Connected", "Static"):
            cleaned_type = "Static"
        self.route_type: str = cleaned_type

        # 4. Validate next-hop
        if self.route_type == "Connected" or next_hop is None or str(next_hop).strip().lower() in ("direct", "none", ""):
            self.next_hop: str = "Direct"
        else:
            cleaned_nh = str(next_hop).strip()
            is_valid, err_msg = IPv6AddressAnalyzer.validate(cleaned_nh)
            if not is_valid:
                raise ValueError(f"Invalid Next Hop IPv6 address '{next_hop}': {err_msg}")
            # Store compressed representation of next hop
            nh_res = analyze_ipv6(cleaned_nh)
            self.next_hop = nh_res.compressed or cleaned_nh

        self.metric: int = int(metric) if isinstance(metric, (int, float)) else 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert route entry to dictionary representation."""
        return {
            "destination_prefix": self.destination_prefix,
            "prefix_length": self.prefix_length,
            "next_hop": self.next_hop,
            "interface": self.interface,
            "route_type": self.route_type,
            "metric": self.metric,
        }

    def __repr__(self) -> str:
        return (
            f"Route(prefix='{self.destination_prefix}', next_hop='{self.next_hop}', "
            f"interface='{self.interface}', type='{self.route_type}')"
        )


class RoutingTable:
    """
    Routing table supporting route storage, management, inspection,
    and Longest Prefix Match (LPM) destination lookups.
    """

    def __init__(self):
        self._routes: List[Route] = []

    def add_route(
        self,
        destination_prefix: str,
        next_hop: Optional[str],
        interface: str,
        route_type: str = "Static",
        metric: int = 1,
    ) -> Route:
        """
        Add or update a route in the routing table.

        Parameters
        ----------
        destination_prefix : str
            Destination IPv6 network (e.g. '2001:db8:4::/64').
        next_hop : Optional[str]
            Next hop IP address or 'Direct' for connected networks.
        interface : str
            Interface name (e.g. 'eth0').
        route_type : str, optional
            'Connected' or 'Static', by default 'Static'
        metric : int, optional
            Route metric, by default 1

        Returns
        -------
        Route
            The newly created and inserted Route object.
        """
        new_route = Route(
            destination_prefix=destination_prefix,
            next_hop=next_hop,
            interface=interface,
            route_type=route_type,
            metric=metric,
        )

        # If identical destination prefix already exists, replace it
        self._routes = [
            r for r in self._routes
            if r.destination_prefix != new_route.destination_prefix
        ]
        self._routes.append(new_route)

        # Keep routes sorted by prefix length descending for clean display and fast lookup
        self._sort_routes()
        return new_route

    def remove_route(self, destination_prefix: str) -> bool:
        """
        Remove a route by its destination prefix.

        Parameters
        ----------
        destination_prefix : str
            The destination prefix to remove.

        Returns
        -------
        bool
            True if a route was found and removed, False otherwise.
        """
        try:
            net = ipaddress.IPv6Network(destination_prefix.strip(), strict=False).compressed
        except Exception:
            net = destination_prefix.strip()

        initial_len = len(self._routes)
        self._routes = [r for r in self._routes if r.destination_prefix != net]
        return len(self._routes) < initial_len

    def remove_interface_routes(self, interface: str) -> int:
        """
        Remove all routes associated with a given interface.

        Parameters
        ----------
        interface : str
            Interface name (e.g. 'eth0').

        Returns
        -------
        int
            Number of routes removed.
        """
        initial_len = len(self._routes)
        self._routes = [r for r in self._routes if r.interface != interface]
        return initial_len - len(self._routes)

    def _sort_routes(self):
        """Sort routes by prefix length descending, then metric ascending."""
        self._routes.sort(key=lambda r: (-r.prefix_length, r.metric, r.destination_prefix))

    @property
    def routes(self) -> List[Route]:
        """Return a copy of all current routes."""
        return list(self._routes)

    def get_matching_routes(self, destination_ip: str) -> List[Route]:
        """
        Find all routes in the table that match the given destination IPv6 address.

        Parameters
        ----------
        destination_ip : str
            Destination IPv6 address (e.g. '2001:db8:4::20').

        Returns
        -------
        List[Route]
            List of matching Route objects sorted by prefix length descending (LPM).
        """
        if not destination_ip or not isinstance(destination_ip, str):
            return []

        cleaned_ip = destination_ip.strip()
        # Handle case where user passes CIDR e.g. 2001:db8:4::20/64
        if "/" in cleaned_ip:
            cleaned_ip = cleaned_ip.split("/")[0].strip()

        try:
            dest_obj = ipaddress.IPv6Address(cleaned_ip)
        except ValueError:
            return []

        matching = [
            route for route in self._routes
            if dest_obj in route.destination_network
        ]

        # Sort matching routes by longest prefix length descending
        matching.sort(key=lambda r: (-r.prefix_length, r.metric))
        return matching

    def find_best_route(self, destination_ip: str) -> Optional[Route]:
        """
        Perform Longest Prefix Match (LPM) to find the best route for the destination.

        Parameters
        ----------
        destination_ip : str
            Destination IPv6 address.

        Returns
        -------
        Optional[Route]
            The best matching Route object with the longest prefix length, or None.
        """
        matching_routes = self.get_matching_routes(destination_ip)
        if matching_routes:
            return matching_routes[0]
        return None

    def display_table(self) -> str:
        """
        Format the routing table as a clean text table.

        Returns
        -------
        str
            Formatted ASCII routing table.
        """
        if not self._routes:
            return "Routing table is empty."

        headers = f"{'Destination Prefix':<22} {'Next Hop':<20} {'Interface':<11} {'Type':<10}"
        separator = "-" * 66

        rows = []
        for route in self._routes:
            rows.append(
                f"{route.destination_prefix:<22} {route.next_hop:<20} {route.interface:<11} {route.route_type:<10}"
            )

        return "\n".join([headers, separator] + rows)

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize all routes to a list of dictionaries."""
        return [r.to_dict() for r in self._routes]

    def __len__(self) -> int:
        return len(self._routes)
