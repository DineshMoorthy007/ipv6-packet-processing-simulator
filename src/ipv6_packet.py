"""
IPv6 Packet & Header Simulation Module - IPv6 Packet Processing Simulator (Phase 2)

This module provides the `IPv6Packet` class and related helpers to construct,
validate, and format simulated IPv6 packets with fixed 40-byte base headers.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union
from src.ipv6_address import IPv6AddressAnalyzer, IPv6AnalysisResult, analyze_ipv6


class NextHeaderProtocol:
    """Standard IPv6 Next Header protocol numbers and resolver utility."""

    PROTOCOLS: Dict[int, str] = {
        0: "Hop-by-Hop Options",
        6: "TCP",
        17: "UDP",
        43: "Routing",
        44: "Fragment",
        50: "ESP",
        51: "AH",
        58: "ICMPv6",
        59: "No Next Header",
        60: "Destination Options",
    }

    # Reverse lookup map for name-based lookup (case-insensitive)
    _NAME_LOOKUP: Dict[str, int] = {
        "hop-by-hop": 0,
        "hopbyhop": 0,
        "hbh": 0,
        "tcp": 6,
        "udp": 17,
        "routing": 43,
        "fragment": 44,
        "frag": 44,
        "esp": 50,
        "ah": 51,
        "icmpv6": 58,
        "icmp6": 58,
        "icmp": 58,
        "no next header": 59,
        "nonextheader": 59,
        "none": 59,
        "destination options": 60,
        "dstopt": 60,
    }

    @classmethod
    def resolve(cls, value: Union[int, str]) -> Tuple[int, str]:
        """
        Resolve a protocol number or protocol name into a validated (number, name) tuple.

        Parameters
        ----------
        value : Union[int, str]
            Protocol name (e.g. 'UDP', 'tcp', 'ICMPv6', 'none') or protocol number (e.g. 17, 6, 58, 59).

        Returns
        -------
        Tuple[int, str]
            (protocol_number, protocol_name)

        Raises
        ------
        ValueError
            If the protocol value is invalid or out of range (0-255).
        """
        if isinstance(value, int):
            proto_num = value
        elif isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Next Header protocol cannot be empty.")

            # Check if string is a numeric string (e.g. "17")
            if cleaned.isdigit() or (cleaned.startswith("-") and cleaned[1:].isdigit()):
                proto_num = int(cleaned)
            else:
                lookup_key = cleaned.lower()
                if lookup_key in cls._NAME_LOOKUP:
                    proto_num = cls._NAME_LOOKUP[lookup_key]
                else:
                    raise ValueError(
                        f"Unknown protocol name '{value}'. Supported names: "
                        f"{', '.join(cls.PROTOCOLS.values())} (or enter protocol number 0-255)."
                    )
        else:
            raise ValueError(f"Invalid Next Header type: {type(value).__name__}. Expected int or str.")

        if not (0 <= proto_num <= 255):
            raise ValueError(f"Next Header protocol number must be between 0 and 255, got {proto_num}.")

        proto_name = cls.PROTOCOLS.get(proto_num, f"Protocol-{proto_num}")
        return proto_num, proto_name


class IPv6Packet:
    """
    Representation of a simulated IPv6 Packet with a fixed 40-byte base header.

    Attributes
    ----------
    version : int
        IPv6 version (always 6).
    traffic_class : int
        Traffic Class / QoS field (0-255).
    flow_label : int
        Flow Label field (0-1048575, 20 bits).
    payload_length : int
        Length of the payload in bytes (calculated automatically).
    next_header : int
        Next Header protocol number (0-255).
    next_header_name : str
        Human-readable Next Header protocol name (e.g. 'UDP', 'TCP', 'ICMPv6').
    hop_limit : int
        Hop Limit field (0-255, default 64).
    source_address : str
        Validated IPv6 source address (compressed representation).
    destination_address : str
        Validated IPv6 destination address (compressed representation).
    source_info : IPv6AnalysisResult
        Analysis result of the source address.
    destination_info : IPv6AnalysisResult
        Analysis result of the destination address.
    payload : str
        Text or string representation of the payload.
    payload_bytes : bytes
        Raw byte sequence of the payload.
    """

    def __init__(
        self,
        source_address: str,
        destination_address: str,
        payload: Union[str, bytes] = "",
        traffic_class: int = 0,
        flow_label: int = 0,
        next_header: Union[int, str] = 17,
        hop_limit: int = 64,
        version: int = 6,
    ):
        """
        Initialize and validate an IPv6 Packet.

        Parameters
        ----------
        source_address : str
            Source IPv6 address.
        destination_address : str
            Destination IPv6 address.
        payload : Union[str, bytes], optional
            Packet payload data, by default ""
        traffic_class : int, optional
            Traffic Class (0-255), by default 0
        flow_label : int, optional
            Flow Label (0-1048575), by default 0
        next_header : Union[int, str], optional
            Next Header protocol name or number, by default 17 (UDP)
        hop_limit : int, optional
            Hop Limit (0-255), by default 64
        version : int, optional
            IP Version, must be 6, by default 6
        """
        # 1. Version Validation
        if version != 6:
            raise ValueError(f"Invalid IPv6 version: {version}. Version must be 6.")
        self.version: int = 6

        # 2. Source & Destination Address Validation (reuse Phase 1 module)
        src_res = analyze_ipv6(str(source_address) if source_address is not None else "")
        if not src_res.is_valid:
            raise ValueError(f"Invalid Source IPv6 Address '{source_address}': {src_res.error_message}")
        self.source_info: IPv6AnalysisResult = src_res
        self.source_address: str = src_res.compressed or str(source_address)

        dst_res = analyze_ipv6(str(destination_address) if destination_address is not None else "")
        if not dst_res.is_valid:
            raise ValueError(f"Invalid Destination IPv6 Address '{destination_address}': {dst_res.error_message}")
        self.destination_info: IPv6AnalysisResult = dst_res
        self.destination_address: str = dst_res.compressed or str(destination_address)

        # 3. Traffic Class Validation (0-255)
        if not isinstance(traffic_class, int) or isinstance(traffic_class, bool):
            try:
                traffic_class = int(traffic_class)
            except (ValueError, TypeError):
                raise ValueError(f"Traffic Class must be an integer between 0 and 255, got '{traffic_class}'.")
        if not (0 <= traffic_class <= 255):
            raise ValueError(f"Traffic Class must be between 0 and 255, got {traffic_class}.")
        self.traffic_class: int = traffic_class

        # 4. Flow Label Validation (0-1048575, 20-bit)
        if not isinstance(flow_label, int) or isinstance(flow_label, bool):
            try:
                flow_label = int(flow_label)
            except (ValueError, TypeError):
                raise ValueError(f"Flow Label must be an integer between 0 and 1048575, got '{flow_label}'.")
        if not (0 <= flow_label <= 1048575):
            raise ValueError(f"Flow Label must be between 0 and 1048575 (20-bit), got {flow_label}.")
        self.flow_label: int = flow_label

        # 5. Next Header Validation
        proto_num, proto_name = NextHeaderProtocol.resolve(next_header)
        self.next_header: int = proto_num
        self.next_header_name: str = proto_name

        # 6. Hop Limit Validation (0-255)
        if not isinstance(hop_limit, int) or isinstance(hop_limit, bool):
            try:
                hop_limit = int(hop_limit)
            except (ValueError, TypeError):
                raise ValueError(f"Hop Limit must be an integer between 0 and 255, got '{hop_limit}'.")
        if not (0 <= hop_limit <= 255):
            raise ValueError(f"Hop Limit must be between 0 and 255, got {hop_limit}.")
        self.hop_limit: int = hop_limit

        # 7. Payload and Payload Length Calculation (in bytes)
        if isinstance(payload, bytes):
            self.payload_bytes: bytes = payload
            try:
                self.payload: str = payload.decode("utf-8")
            except UnicodeDecodeError:
                self.payload: str = str(payload)
        elif isinstance(payload, str):
            self.payload: str = payload
            self.payload_bytes: bytes = payload.encode("utf-8")
        else:
            payload_str = str(payload)
            self.payload = payload_str
            self.payload_bytes = payload_str.encode("utf-8")

        self.payload_length: int = len(self.payload_bytes)

    def display_header(self) -> str:
        """
        Format the IPv6 packet header and payload for visual terminal display.

        Returns
        -------
        str
            Formatted textual representation of the simulated IPv6 packet.
        """
        lines = [
            "IPv6 PACKET",
            "=" * 40,
            "IPv6 Header",
            "-" * 40,
            f"Version         : {self.version}",
            f"Traffic Class   : {self.traffic_class}",
            f"Flow Label      : {self.flow_label}",
            f"Payload Length  : {self.payload_length} bytes",
            f"Next Header     : {self.next_header_name} ({self.next_header})",
            f"Hop Limit       : {self.hop_limit}",
            "",
            "Source Address",
            f"{self.source_address}",
            "",
            "Destination Address",
            f"{self.destination_address}",
            "-" * 40,
            "Payload",
            f"{self.payload if self.payload else '<Empty Payload>'}",
            "=" * 40,
        ]
        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a concise summary dictionary of key packet fields for forwarding and routing.

        Returns
        -------
        Dict[str, Any]
            Packet summary containing Source, Destination, Payload, Payload length, Next Header, and Hop Limit.
        """
        return {
            "source": self.source_address,
            "destination": self.destination_address,
            "payload": self.payload,
            "payload_length": self.payload_length,
            "next_header": f"{self.next_header_name} ({self.next_header})",
            "hop_limit": self.hop_limit,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the complete IPv6 packet into a dictionary.

        Returns
        -------
        Dict[str, Any]
            Full dictionary of packet properties and header fields.
        """
        return {
            "version": self.version,
            "traffic_class": self.traffic_class,
            "flow_label": self.flow_label,
            "payload_length_bytes": self.payload_length,
            "next_header_number": self.next_header,
            "next_header_name": self.next_header_name,
            "hop_limit": self.hop_limit,
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "source_type": self.source_info.address_type,
            "destination_type": self.destination_info.address_type,
            "payload": self.payload,
            "total_packet_size_bytes": 40 + self.payload_length,  # Base IPv6 header is 40 bytes
        }

    def __repr__(self) -> str:
        return (
            f"IPv6Packet(src='{self.source_address}', dst='{self.destination_address}', "
            f"proto={self.next_header_name}({self.next_header}), len={self.payload_length}B, "
            f"hop_limit={self.hop_limit})"
        )


def create_ipv6_packet(
    source_address: str,
    destination_address: str,
    payload: Union[str, bytes] = "",
    traffic_class: int = 0,
    flow_label: int = 0,
    next_header: Union[int, str] = "UDP",
    hop_limit: int = 64,
) -> IPv6Packet:
    """
    Factory function to validate and construct an IPv6Packet instance.

    Parameters
    ----------
    source_address : str
        Source IPv6 address.
    destination_address : str
        Destination IPv6 address.
    payload : Union[str, bytes], optional
        Payload data, by default ""
    traffic_class : int, optional
        Traffic Class (0-255), by default 0
    flow_label : int, optional
        Flow Label (0-1048575), by default 0
    next_header : Union[int, str], optional
        Next Header protocol (name or number), by default 'UDP'
    hop_limit : int, optional
        Hop Limit (0-255), by default 64

    Returns
    -------
    IPv6Packet
        The created and validated IPv6Packet object.
    """
    return IPv6Packet(
        source_address=source_address,
        destination_address=destination_address,
        payload=payload,
        traffic_class=traffic_class,
        flow_label=flow_label,
        next_header=next_header,
        hop_limit=hop_limit,
    )
