"""
IPv6 Address Module - IPv6 Packet Processing Simulator (Phase 1)

This module provides comprehensive parsing, validation, classification,
representation, and subnet analysis for IPv6 addresses and networks using
Python's built-in `ipaddress` module.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# Known IPv6 special networks for classification
IPV6_DOCUMENTATION_NET = ipaddress.IPv6Network("2001:db8::/32")
IPV6_BENCHMARKING_NET = ipaddress.IPv6Network("2001:2::/48")
IPV6_6TO4_NET = ipaddress.IPv6Network("2002::/16")
IPV6_TEREDO_NET = ipaddress.IPv6Network("2001::/32")
IPV6_DISCARD_NET = ipaddress.IPv6Network("100::/64")
IPV6_UNIQUE_LOCAL_NET = ipaddress.IPv6Network("fc00::/7")


@dataclass
class IPv6AnalysisResult:
    """Data container holding comprehensive analysis results for an IPv6 address/network."""

    raw_input: str
    is_valid: bool
    error_message: Optional[str] = None

    # Address representations
    address_obj: Optional[ipaddress.IPv6Address] = None
    interface_obj: Optional[ipaddress.IPv6Interface] = None
    network_obj: Optional[ipaddress.IPv6Network] = None

    compressed: Optional[str] = None
    expanded: Optional[str] = None
    integer_value: Optional[int] = None
    hex_value: Optional[str] = None
    binary_representation: Optional[str] = None

    # Classification
    address_type: Optional[str] = None
    type_tags: List[str] = field(default_factory=list)
    scope: Optional[str] = None

    # Network / Prefix properties
    bit_length: int = 128
    has_prefix: bool = False
    prefix_length: Optional[int] = None
    network_address: Optional[str] = None
    network_cidr: Optional[str] = None
    netmask: Optional[str] = None
    hostmask: Optional[str] = None
    interface_identifier: Optional[str] = None
    host_portion: Optional[str] = None
    total_addresses: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert the analysis result to a serializable dictionary."""
        return {
            "raw_input": self.raw_input,
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "compressed": self.compressed,
            "expanded": self.expanded,
            "integer_value": self.integer_value,
            "hex_value": self.hex_value,
            "binary_representation": self.binary_representation,
            "address_type": self.address_type,
            "type_tags": self.type_tags,
            "scope": self.scope,
            "bit_length": self.bit_length,
            "has_prefix": self.has_prefix,
            "prefix_length": self.prefix_length,
            "network_address": self.network_address,
            "network_cidr": self.network_cidr,
            "netmask": self.netmask,
            "hostmask": self.hostmask,
            "interface_identifier": self.interface_identifier,
            "host_portion": self.host_portion,
            "total_addresses": self.total_addresses,
        }


class IPv6AddressAnalyzer:
    """Analyzer class for validating and breaking down IPv6 addresses and networks."""

    @staticmethod
    def validate(ip_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate whether a string is a valid IPv6 address or IPv6 interface/network notation.

        Parameters
        ----------
        ip_str : str
            The input IPv6 address string (e.g. '2001:db8::1' or '2001:db8::1/64').

        Returns
        -------
        Tuple[bool, Optional[str]]
            A tuple of (is_valid, error_message).
        """
        if not isinstance(ip_str, str):
            return False, "Input must be a string."

        cleaned = ip_str.strip()
        if not cleaned:
            return False, "Address input cannot be empty."

        try:
            # First check if it contains CIDR notation
            if "/" in cleaned:
                # Use IPv6Interface to validate address + prefix length
                ipaddress.IPv6Interface(cleaned)
            else:
                ipaddress.IPv6Address(cleaned)
            return True, None
        except ipaddress.AddressValueError as err:
            return False, f"Invalid IPv6 address format: {err}"
        except ipaddress.NetmaskValueError as err:
            return False, f"Invalid IPv6 prefix length/netmask: {err}"
        except Exception as err:
            return False, f"Validation error: {err}"

    @classmethod
    def classify_address(cls, addr: ipaddress.IPv6Address) -> Tuple[str, List[str], str]:
        """
        Determine the classification, detailed tags, and scope of an IPv6 address.

        Parameters
        ----------
        addr : ipaddress.IPv6Address
            The parsed IPv6 address object.

        Returns
        -------
        Tuple[str, List[str], str]
            (primary_type_description, list_of_tags, scope_description)
        """
        tags = []
        primary_type = "Unknown"
        scope = "Unspecified"

        if addr.is_loopback:
            primary_type = "Loopback"
            tags.append("Loopback (::1/128)")
            scope = "Node-Local"

        elif addr.is_unspecified:
            primary_type = "Unspecified"
            tags.append("Unspecified (::/128)")
            scope = "None"

        elif addr.is_multicast:
            primary_type = "Multicast"
            tags.append("Multicast (ff00::/8)")
            # Analyze multicast scope from 2nd byte lower 4 bits
            # Format: ff0<scope>::
            scope_bits = (addr.exploded.replace(":", "")[3]).lower()
            scope_names = {
                "1": "Interface-Local / Node-Local",
                "2": "Link-Local",
                "4": "Admin-Local",
                "5": "Site-Local",
                "8": "Organization-Local",
                "e": "Global",
            }
            scope = f"Multicast ({scope_names.get(scope_bits, f'Scope {scope_bits}')})"

        elif addr.is_link_local:
            primary_type = "Link-Local"
            tags.append("Link-Local Unicast (fe80::/10)")
            scope = "Link-Local"

        elif addr in IPV6_UNIQUE_LOCAL_NET:
            primary_type = "Unique Local (Private)"
            tags.append("Unique Local Address (fc00::/7)")
            scope = "Global / Organization-Local"

        elif addr in IPV6_DOCUMENTATION_NET:
            primary_type = "Global/Documentation"
            tags.extend(["Global Unicast (2000::/3)", "Documentation Prefix (2001:db8::/32)"])
            scope = "Documentation / Non-Routable"

        elif addr in IPV6_BENCHMARKING_NET:
            primary_type = "Benchmarking"
            tags.append("Benchmarking (2001:2::/48)")
            scope = "Benchmarking"

        elif addr.is_reserved:
            primary_type = "Reserved"
            tags.append("IETF Reserved")
            scope = "Reserved"

        elif addr.is_global:
            primary_type = "Global Unicast"
            tags.append("Global Unicast (2000::/3)")
            scope = "Global Internet"

        else:
            primary_type = "Special / Reserved"
            tags.append("Reserved / Other")
            scope = "Special"

        # Additional secondary tags
        if addr.ipv4_mapped:
            tags.append(f"IPv4-Mapped ({addr.ipv4_mapped})")

        return primary_type, tags, scope

    @classmethod
    def analyze(cls, ip_str: str) -> IPv6AnalysisResult:
        """
        Perform a full analysis on an IPv6 address or network string.

        Parameters
        ----------
        ip_str : str
            The input IPv6 address or CIDR notation.

        Returns
        -------
        IPv6AnalysisResult
            Structured result containing all extracted properties.
        """
        is_valid, err_msg = cls.validate(ip_str)
        if not is_valid:
            return IPv6AnalysisResult(
                raw_input=str(ip_str),
                is_valid=False,
                error_message=err_msg,
            )

        cleaned = ip_str.strip()
        has_prefix = "/" in cleaned

        try:
            if has_prefix:
                interface = ipaddress.IPv6Interface(cleaned)
                address = interface.ip
                network = interface.network
                prefix_len = interface.network.prefixlen
            else:
                address = ipaddress.IPv6Address(cleaned)
                interface = None
                network = None
                prefix_len = None

            # Representation values
            compressed = address.compressed
            expanded = address.exploded
            int_val = int(address)
            hex_val = f"0x{int_val:032x}"
            # Binary string formatted in 8 16-bit blocks separated by colons
            bin_raw = f"{int_val:0128b}"
            binary_repr = ":".join(bin_raw[i : i + 16] for i in range(0, 128, 16))

            # Classification
            primary_type, tags, scope = cls.classify_address(address)

            # Subnet properties
            network_addr_str = None
            network_cidr_str = None
            netmask_str = None
            hostmask_str = None
            host_portion_str = None
            interface_id_str = None
            total_addrs = None

            if has_prefix and network:
                network_addr_str = network.network_address.compressed
                network_cidr_str = network.compressed
                netmask_str = network.netmask.compressed
                hostmask_str = network.hostmask.compressed
                total_addrs = network.num_addresses

                # Interface identifier calculation (lowest 64 bits formatted)
                # Standard IPv6 interface ID is 64 bits
                host_int = int_val & int(network.hostmask)
                host_portion_str = str(ipaddress.IPv6Address(host_int).compressed)

                if prefix_len <= 64:
                    iid_int = int_val & 0xFFFFFFFFFFFFFFFF
                    interface_id_str = f"{(iid_int >> 48) & 0xFFFF:04x}:{(iid_int >> 32) & 0xFFFF:04x}:{(iid_int >> 16) & 0xFFFF:04x}:{iid_int & 0xFFFF:04x}"

            return IPv6AnalysisResult(
                raw_input=cleaned,
                is_valid=True,
                address_obj=address,
                interface_obj=interface,
                network_obj=network,
                compressed=compressed,
                expanded=expanded,
                integer_value=int_val,
                hex_value=hex_val,
                binary_representation=binary_repr,
                address_type=primary_type,
                type_tags=tags,
                scope=scope,
                bit_length=128,
                has_prefix=has_prefix,
                prefix_length=prefix_len,
                network_address=network_addr_str,
                network_cidr=network_cidr_str,
                netmask=netmask_str,
                hostmask=hostmask_str,
                interface_identifier=interface_id_str,
                host_portion=host_portion_str,
                total_addresses=total_addrs,
            )

        except Exception as err:
            return IPv6AnalysisResult(
                raw_input=cleaned,
                is_valid=False,
                error_message=f"Processing error: {err}",
            )

    @classmethod
    def format_report(cls, result: IPv6AnalysisResult) -> str:
        """
        Generate a clean, structured textual report for display.

        Parameters
        ----------
        result : IPv6AnalysisResult
            The analysis result object.

        Returns
        -------
        str
            The formatted output report.
        """
        lines = []
        lines.append("## IPv6 Address Analysis\n")
        lines.append(f"Input Address : {result.raw_input}")

        if not result.is_valid:
            lines.append("Valid IPv6    : No")
            lines.append(f"Error         : {result.error_message}")
            return "\n".join(lines)

        lines.append("Valid IPv6    : Yes")
        lines.append(f"Compressed    : {result.compressed}")
        lines.append(f"Expanded      : {result.expanded}")
        lines.append(f"Address Type  : {result.address_type}")
        lines.append(f"Bit Length    : {result.bit_length}")

        if result.has_prefix:
            lines.append("")
            lines.append("--- Network / Subnet Details ---")
            lines.append(f"Network       : {result.network_cidr}")
            lines.append(f"Prefix Length : {result.prefix_length}")
            lines.append(f"Network Addr  : {result.network_address}")
            lines.append(f"Netmask       : {result.netmask}")
            if result.host_portion:
                lines.append(f"Host Portion  : {result.host_portion}")
            if result.interface_identifier:
                lines.append(f"Interface ID  : {result.interface_identifier}")
            if result.total_addresses is not None:
                if result.prefix_length <= 64:
                    lines.append(f"Total Hosts   : 2^{128 - result.prefix_length} ({result.total_addresses:,} addresses)")
                else:
                    lines.append(f"Total Hosts   : {result.total_addresses:,} addresses")

        return "\n".join(lines)


# Convenient module-level functions
def validate_ipv6(address_str: str) -> bool:
    """Validate an IPv6 address string."""
    is_valid, _ = IPv6AddressAnalyzer.validate(address_str)
    return is_valid


def analyze_ipv6(address_str: str) -> IPv6AnalysisResult:
    """Analyze an IPv6 address or network string."""
    return IPv6AddressAnalyzer.analyze(address_str)
