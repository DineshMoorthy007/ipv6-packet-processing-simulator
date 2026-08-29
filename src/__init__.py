"""
IPv6 Packet Processing Simulator - Core Package.

Phase 1: IPv6 Addressing & Project Foundation.
"""

from src.ipv6_address import (
    IPv6AddressAnalyzer,
    IPv6AnalysisResult,
    analyze_ipv6,
    validate_ipv6,
)

__all__ = [
    "IPv6AddressAnalyzer",
    "IPv6AnalysisResult",
    "analyze_ipv6",
    "validate_ipv6",
]
