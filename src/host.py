"""
Simulated IPv6 Host & Link Module - IPv6 Packet Processing Simulator (Phase 6)

This module defines the `Host` and `Link` classes representing end-user devices
and point-to-point/broadcast subnet connections in an IPv6 network.
"""

from __future__ import annotations

import ipaddress
from typing import Any, Dict, Optional
from src.ipv6_address import analyze_ipv6


class Host:
    """
    Representation of an end-host device in the simulated IPv6 network.

    Attributes
    ----------
    name : str
        Host identifier (e.g. 'Host A', 'Host B').
    ipv6_address : str
        Assigned IPv6 address.
    prefix_length : int
        Subnet prefix length in bits (e.g. 64).
    network : str
        Connected subnet CIDR (e.g. '2001:db8:1::/64').
    default_gateway : Optional[str]
        Default router gateway IPv6 address.
    interface : str
        Local network interface name (e.g. 'eth0').
    """

    def __init__(
        self,
        name: str,
        ipv6_address_cidr: str,
        default_gateway: Optional[str] = None,
        interface: str = "eth0",
    ):
        if not name or not isinstance(name, str):
            raise ValueError("Host name must be a non-empty string.")
        self.name: str = name.strip()

        if not ipv6_address_cidr or not isinstance(ipv6_address_cidr, str):
            raise ValueError("Host IPv6 address/CIDR must be a non-empty string.")

        cleaned_cidr = ipv6_address_cidr.strip()
        if "/" not in cleaned_cidr:
            cleaned_cidr = f"{cleaned_cidr}/64"

        try:
            intf_obj = ipaddress.IPv6Interface(cleaned_cidr)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as err:
            raise ValueError(f"Invalid host IPv6 address '{ipv6_address_cidr}': {err}")

        self.ipv6_address: str = intf_obj.ip.compressed
        self.network: str = intf_obj.network.compressed
        self.prefix_length: int = intf_obj.network.prefixlen
        self.interface: str = interface.strip() if interface else "eth0"

        if default_gateway:
            gw_res = analyze_ipv6(default_gateway.strip())
            if not gw_res.is_valid:
                raise ValueError(f"Invalid default gateway IPv6 address '{default_gateway}': {gw_res.error_message}")
            self.default_gateway: Optional[str] = gw_res.compressed or default_gateway.strip()
        else:
            self.default_gateway = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert host configuration to dictionary."""
        return {
            "name": self.name,
            "ipv6_address": f"{self.ipv6_address}/{self.prefix_length}",
            "network": self.network,
            "default_gateway": self.default_gateway,
            "interface": self.interface,
        }

    def __repr__(self) -> str:
        return f"Host(name='{self.name}', ip='{self.ipv6_address}/{self.prefix_length}', gw='{self.default_gateway}')"


class Link:
    """
    Representation of a point-to-point or broadcast link between two network nodes.

    Attributes
    ----------
    node_a : str
        Name of the first node.
    interface_a : str
        Interface name on node A.
    node_b : str
        Name of the second node.
    interface_b : str
        Interface name on node B.
    network : str
        Subnet prefix in CIDR notation for the link.
    """

    def __init__(self, node_a: str, interface_a: str, node_b: str, interface_b: str, network: str):
        if not node_a or not node_b:
            raise ValueError("Link nodes must be non-empty strings.")
        self.node_a: str = node_a.strip()
        self.interface_a: str = interface_a.strip() if interface_a else "eth0"
        self.node_b: str = node_b.strip()
        self.interface_b: str = interface_b.strip() if interface_b else "eth0"

        try:
            self.network: str = ipaddress.IPv6Network(network.strip(), strict=False).compressed
        except Exception as err:
            raise ValueError(f"Invalid link network '{network}': {err}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert link configuration to dictionary."""
        return {
            "node_a": self.node_a,
            "interface_a": self.interface_a,
            "node_b": self.node_b,
            "interface_b": self.interface_b,
            "network": self.network,
        }

    def __repr__(self) -> str:
        return (
            f"Link({self.node_a}:{self.interface_a} <--> {self.node_b}:{self.interface_b} "
            f"on {self.network})"
        )
