"""
Unit tests for IPv6 Address module (Phase 1).
"""

import pytest
from src.ipv6_address import (
    IPv6AddressAnalyzer,
    IPv6AnalysisResult,
    analyze_ipv6,
    validate_ipv6,
)


class TestIPv6Validation:
    """Tests for IPv6 address validation."""

    @pytest.mark.parametrize(
        "valid_address",
        [
            "2001:db8:1::10",
            "2001:0db8:0001:0000:0000:0000:0000:0010",
            "::1",
            "::",
            "fe80::1",
            "fe80::200:5aee:feaa:20a2",
            "ff02::1",
            "fd00::1",
            "2001:db8:1::10/64",
            "fe80::1/10",
            "::1/128",
            "2001:db8::/32",
            "  2001:db8::1  ",  # handles whitespace
        ],
    )
    def test_valid_ipv6_addresses(self, valid_address):
        """Test that valid IPv6 addresses are recognized as valid."""
        assert validate_ipv6(valid_address) is True
        is_valid, err = IPv6AddressAnalyzer.validate(valid_address)
        assert is_valid is True
        assert err is None

    @pytest.mark.parametrize(
        "invalid_address",
        [
            "2001:db8:::1",          # triple colon
            "2001:xyz::1",           # invalid hex character
            "192.168.1.1",           # IPv4 address without IPv6 mapping
            "2001:db8:1:2:3:4:5:6:7",# 9 groups
            "2001:db8::1/129",       # prefix > 128
            "2001:db8::1/-1",        # negative prefix
            "2001:db8::1/abc",       # non-numeric prefix
            "",                      # empty string
            "   ",                   # whitespace only
            "12345",                 # plain number
            None,                    # None input
            123,                     # non-string
        ],
    )
    def test_invalid_ipv6_addresses(self, invalid_address):
        """Test that invalid IPv6 addresses are caught with error messages."""
        assert validate_ipv6(invalid_address) is False
        is_valid, err = IPv6AddressAnalyzer.validate(invalid_address)
        assert is_valid is False
        assert err is not None


class TestIPv6Representations:
    """Tests for compressed, expanded, and binary representations."""

    def test_compressed_representation(self):
        """Test RFC 5952 compression."""
        res = analyze_ipv6("2001:0db8:0001:0000:0000:0000:0000:0010")
        assert res.is_valid is True
        assert res.compressed == "2001:db8:1::10"

    def test_expanded_representation(self):
        """Test full 8-group expanded representation."""
        res = analyze_ipv6("2001:db8:1::10")
        assert res.is_valid is True
        assert res.expanded == "2001:0db8:0001:0000:0000:0000:0000:0010"

    def test_loopback_expanded_and_compressed(self):
        """Test ::1 representation."""
        res = analyze_ipv6("::1")
        assert res.is_valid is True
        assert res.compressed == "::1"
        assert res.expanded == "0000:0000:0000:0000:0000:0000:0000:0001"
        assert res.integer_value == 1

    def test_unspecified_expanded_and_compressed(self):
        """Test :: representation."""
        res = analyze_ipv6("::")
        assert res.is_valid is True
        assert res.compressed == "::"
        assert res.expanded == "0000:0000:0000:0000:0000:0000:0000:0000"
        assert res.integer_value == 0

    def test_binary_and_hex_representation(self):
        """Test bit length, integer, and binary conversion."""
        res = analyze_ipv6("::1")
        assert res.bit_length == 128
        assert res.hex_value == "0x00000000000000000000000000000001"
        assert res.binary_representation == "0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000001"


class TestIPv6Classification:
    """Tests for IPv6 address classification."""

    def test_loopback_classification(self):
        """Test loopback address classification."""
        res = analyze_ipv6("::1")
        assert res.address_type == "Loopback"
        assert "Loopback (::1/128)" in res.type_tags
        assert res.scope == "Node-Local"

    def test_unspecified_classification(self):
        """Test unspecified address classification."""
        res = analyze_ipv6("::")
        assert res.address_type == "Unspecified"
        assert "Unspecified (::/128)" in res.type_tags

    def test_link_local_classification(self):
        """Test link-local address classification."""
        res = analyze_ipv6("fe80::1")
        assert res.address_type == "Link-Local"
        assert "Link-Local Unicast (fe80::/10)" in res.type_tags
        assert res.scope == "Link-Local"

    def test_multicast_classification(self):
        """Test multicast address classification."""
        res = analyze_ipv6("ff02::1")
        assert res.address_type == "Multicast"
        assert "Multicast (ff00::/8)" in res.type_tags
        assert "Link-Local" in res.scope

    def test_documentation_classification(self):
        """Test documentation prefix 2001:db8::/32 classification."""
        res = analyze_ipv6("2001:db8:1::10")
        assert res.address_type == "Global/Documentation"
        assert any("Documentation" in tag for tag in res.type_tags)

    def test_unique_local_classification(self):
        """Test unique local (private) classification."""
        res = analyze_ipv6("fd12:3456:789a:1::1")
        assert res.address_type == "Unique Local (Private)"
        assert any("Unique Local" in tag for tag in res.type_tags)

    def test_global_unicast_classification(self):
        """Test standard global unicast address."""
        res = analyze_ipv6("2607:f8b0:4005:805::200e")
        assert res.address_type == "Global Unicast"
        assert res.scope == "Global Internet"


class TestIPv6SubnetAnalysis:
    """Tests for prefix and subnet calculations."""

    def test_slash_64_subnet_calculation(self):
        """Test /64 network calculation."""
        res = analyze_ipv6("2001:db8:1::10/64")
        assert res.is_valid is True
        assert res.has_prefix is True
        assert res.prefix_length == 64
        assert res.network_address == "2001:db8:1::"
        assert res.network_cidr == "2001:db8:1::/64"
        assert res.netmask == "ffff:ffff:ffff:ffff::"
        assert res.hostmask == "::ffff:ffff:ffff:ffff"
        assert res.host_portion == "::10"
        assert res.interface_identifier == "0000:0000:0000:0010"
        assert res.total_addresses == 2**64

    def test_slash_48_subnet_calculation(self):
        """Test /48 network calculation."""
        res = analyze_ipv6("2001:db8:abcd:1234::1/48")
        assert res.is_valid is True
        assert res.prefix_length == 48
        assert res.network_address == "2001:db8:abcd::"
        assert res.total_addresses == 2**80

    def test_slash_128_host_route(self):
        """Test /128 single host prefix calculation."""
        res = analyze_ipv6("2001:db8::1/128")
        assert res.is_valid is True
        assert res.prefix_length == 128
        assert res.network_address == "2001:db8::1"
        assert res.total_addresses == 1


class TestOutputFormattingAndHelpers:
    """Tests for report formatting and helper methods."""

    def test_format_report_valid_plain_address(self):
        """Test formatting of standard valid address."""
        res = analyze_ipv6("2001:db8:1::10")
        report = IPv6AddressAnalyzer.format_report(res)
        assert "## IPv6 Address Analysis" in report
        assert "Input Address : 2001:db8:1::10" in report
        assert "Valid IPv6    : Yes" in report
        assert "Compressed    : 2001:db8:1::10" in report
        assert "Expanded      : 2001:0db8:0001:0000:0000:0000:0000:0010" in report
        assert "Address Type  : Global/Documentation" in report
        assert "Bit Length    : 128" in report

    def test_format_report_valid_network(self):
        """Test formatting of network address with prefix."""
        res = analyze_ipv6("2001:db8:1::10/64")
        report = IPv6AddressAnalyzer.format_report(res)
        assert "Network       : 2001:db8:1::/64" in report
        assert "Prefix Length : 64" in report
        assert "Network Addr  : 2001:db8:1::" in report

    def test_format_report_invalid_address(self):
        """Test formatting of invalid address does not crash and prints error."""
        res = analyze_ipv6("2001:xyz::1")
        assert res.is_valid is False
        report = IPv6AddressAnalyzer.format_report(res)
        assert "Valid IPv6    : No" in report
        assert "Error         :" in report

    def test_to_dict_method(self):
        """Test serialization to dictionary."""
        res = analyze_ipv6("2001:db8:1::10/64")
        data = res.to_dict()
        assert isinstance(data, dict)
        assert data["is_valid"] is True
        assert data["prefix_length"] == 64
        assert data["compressed"] == "2001:db8:1::10"
