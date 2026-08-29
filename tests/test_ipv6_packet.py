"""
Unit tests for IPv6 Packet and Header Simulation module (Phase 2).
"""

import pytest
from src.ipv6_packet import (
    IPv6Packet,
    NextHeaderProtocol,
    create_ipv6_packet,
)


class TestIPv6PacketCreation:
    """Tests for packet creation and default properties."""

    def test_successful_packet_creation_defaults(self):
        """Test creating a valid packet with default header options."""
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )

        assert pkt.version == 6
        assert pkt.source_address == "2001:db8:1::10"
        assert pkt.destination_address == "2001:db8:4::20"
        assert pkt.payload == "Hello IPv6"
        assert pkt.payload_length == 10
        assert pkt.traffic_class == 0
        assert pkt.flow_label == 0
        assert pkt.next_header == 17
        assert pkt.next_header_name == "UDP"
        assert pkt.hop_limit == 64

    def test_version_must_be_six(self):
        """Test that IPv6 version is strictly 6 and rejecting any other version."""
        with pytest.raises(ValueError, match="Invalid IPv6 version: 4"):
            IPv6Packet(
                source_address="2001:db8:1::10",
                destination_address="2001:db8:4::20",
                version=4,
            )


class TestAddressValidationInPacket:
    """Tests for source and destination IPv6 address validation during packet creation."""

    def test_valid_addresses(self):
        """Test packet creation with various valid IPv6 address formats."""
        pkt = create_ipv6_packet(
            source_address="fe80::1",
            destination_address="ff02::1",
            payload="Ping",
            next_header="ICMPv6",
        )
        assert pkt.source_address == "fe80::1"
        assert pkt.destination_address == "ff02::1"
        assert pkt.source_info.address_type == "Link-Local"
        assert pkt.destination_info.address_type == "Multicast"

    def test_invalid_source_address(self):
        """Test rejection of invalid source address."""
        with pytest.raises(ValueError, match="Invalid Source IPv6 Address"):
            create_ipv6_packet(
                source_address="2001:invalid_hex::1",
                destination_address="2001:db8::2",
                payload="Test",
            )

    def test_invalid_destination_address(self):
        """Test rejection of invalid destination address."""
        with pytest.raises(ValueError, match="Invalid Destination IPv6 Address"):
            create_ipv6_packet(
                source_address="2001:db8::1",
                destination_address="192.168.1.1",  # IPv4 invalid for IPv6 packet
                payload="Test",
            )


class TestHeaderFieldsValidation:
    """Tests for Traffic Class, Flow Label, Hop Limit, and Next Header validation."""

    @pytest.mark.parametrize("tc", [0, 64, 128, 255])
    def test_valid_traffic_class(self, tc):
        """Test valid Traffic Class values."""
        pkt = create_ipv6_packet(
            source_address="2001:db8::1",
            destination_address="2001:db8::2",
            traffic_class=tc,
        )
        assert pkt.traffic_class == tc

    @pytest.mark.parametrize("invalid_tc", [-1, 256, 1000, "invalid"])
    def test_invalid_traffic_class(self, invalid_tc):
        """Test rejection of out-of-range or invalid Traffic Class."""
        with pytest.raises(ValueError, match="Traffic Class"):
            create_ipv6_packet(
                source_address="2001:db8::1",
                destination_address="2001:db8::2",
                traffic_class=invalid_tc,
            )

    @pytest.mark.parametrize("fl", [0, 100, 524288, 1048575])
    def test_valid_flow_label(self, fl):
        """Test valid Flow Label values (0 to 2^20 - 1)."""
        pkt = create_ipv6_packet(
            source_address="2001:db8::1",
            destination_address="2001:db8::2",
            flow_label=fl,
        )
        assert pkt.flow_label == fl

    @pytest.mark.parametrize("invalid_fl", [-1, 1048576, 2000000, "abc"])
    def test_invalid_flow_label(self, invalid_fl):
        """Test rejection of out-of-range or invalid Flow Label."""
        with pytest.raises(ValueError, match="Flow Label"):
            create_ipv6_packet(
                source_address="2001:db8::1",
                destination_address="2001:db8::2",
                flow_label=invalid_fl,
            )

    @pytest.mark.parametrize("hl", [0, 1, 64, 128, 255])
    def test_valid_hop_limit(self, hl):
        """Test valid Hop Limit values."""
        pkt = create_ipv6_packet(
            source_address="2001:db8::1",
            destination_address="2001:db8::2",
            hop_limit=hl,
        )
        assert pkt.hop_limit == hl

    @pytest.mark.parametrize("invalid_hl", [-1, 256, 500, "none"])
    def test_invalid_hop_limit(self, invalid_hl):
        """Test rejection of out-of-range or invalid Hop Limit."""
        with pytest.raises(ValueError, match="Hop Limit"):
            create_ipv6_packet(
                source_address="2001:db8::1",
                destination_address="2001:db8::2",
                hop_limit=invalid_hl,
            )


class TestNextHeaderProtocols:
    """Tests for Next Header protocol resolution by name and number."""

    def test_tcp_next_header(self):
        """Test TCP next header by name and number."""
        pkt_by_name = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header="TCP")
        assert pkt_by_name.next_header == 6
        assert pkt_by_name.next_header_name == "TCP"

        pkt_by_num = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header=6)
        assert pkt_by_num.next_header == 6
        assert pkt_by_num.next_header_name == "TCP"

    def test_udp_next_header(self):
        """Test UDP next header by name and number."""
        pkt_by_name = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header="udp")
        assert pkt_by_name.next_header == 17
        assert pkt_by_name.next_header_name == "UDP"

        pkt_by_num = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header=17)
        assert pkt_by_num.next_header == 17
        assert pkt_by_num.next_header_name == "UDP"

    def test_icmpv6_next_header(self):
        """Test ICMPv6 next header by name and number."""
        pkt_by_name = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header="ICMPv6")
        assert pkt_by_name.next_header == 58
        assert pkt_by_name.next_header_name == "ICMPv6"

        pkt_by_num = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header=58)
        assert pkt_by_num.next_header == 58
        assert pkt_by_num.next_header_name == "ICMPv6"

    def test_no_next_header(self):
        """Test No Next Header (59) by name and number."""
        pkt_by_name = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header="No Next Header")
        assert pkt_by_name.next_header == 59
        assert pkt_by_name.next_header_name == "No Next Header"

        pkt_by_none = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header="none")
        assert pkt_by_none.next_header == 59

        pkt_by_num = create_ipv6_packet("2001:db8::1", "2001:db8::2", next_header=59)
        assert pkt_by_num.next_header == 59
        assert pkt_by_num.next_header_name == "No Next Header"

    def test_invalid_next_header_protocol(self):
        """Test rejection of unknown or out-of-range protocol."""
        with pytest.raises(ValueError, match="Unknown protocol name"):
            NextHeaderProtocol.resolve("UNKNOWN_PROTOCOL_XYZ")

        with pytest.raises(ValueError, match="between 0 and 255"):
            NextHeaderProtocol.resolve(300)


class TestPayloadLengthCalculation:
    """Tests for byte-accurate payload length calculations."""

    def test_empty_payload(self):
        """Test empty payload length is 0 bytes."""
        pkt = create_ipv6_packet("2001:db8::1", "2001:db8::2", payload="")
        assert pkt.payload_length == 0
        assert pkt.payload_bytes == b""

    def test_ascii_payload(self):
        """Test standard ASCII payload length."""
        pkt = create_ipv6_packet("2001:db8::1", "2001:db8::2", payload="Hello IPv6")
        assert pkt.payload_length == 10
        assert pkt.payload_bytes == b"Hello IPv6"

    def test_multibyte_unicode_payload(self):
        """Test multi-byte UTF-8 character length in bytes."""
        # 🌐 (globe) is 4 bytes in UTF-8: 10 + 4 + 1 + 6 = 21 bytes
        unicode_text = "IPv6 Test 🌐 Packet"
        pkt = create_ipv6_packet("2001:db8::1", "2001:db8::2", payload=unicode_text)
        expected_bytes = unicode_text.encode("utf-8")
        assert pkt.payload_length == len(expected_bytes)
        assert pkt.payload_bytes == expected_bytes

    def test_raw_bytes_payload(self):
        """Test providing raw bytes payload."""
        raw_bytes = bytes([0x01, 0x02, 0x03, 0x04, 0x05])
        pkt = create_ipv6_packet("2001:db8::1", "2001:db8::2", payload=raw_bytes)
        assert pkt.payload_length == 5
        assert pkt.payload_bytes == raw_bytes


class TestPacketDisplayAndSummary:
    """Tests for packet output formatting, summary, and serialization."""

    def test_display_header_format(self):
        """Test display_header matches the required format."""
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )
        display = pkt.display_header()

        assert "IPv6 PACKET" in display
        assert "Version         : 6" in display
        assert "Traffic Class   : 0" in display
        assert "Flow Label      : 0" in display
        assert "Payload Length  : 10 bytes" in display
        assert "Next Header     : UDP (17)" in display
        assert "Hop Limit       : 64" in display
        assert "Source Address\n2001:db8:1::10" in display
        assert "Destination Address\n2001:db8:4::20" in display
        assert "Payload\nHello IPv6" in display

    def test_get_summary(self):
        """Test get_summary returns concise dictionary."""
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )
        summary = pkt.get_summary()

        assert summary["source"] == "2001:db8:1::10"
        assert summary["destination"] == "2001:db8:4::20"
        assert summary["payload"] == "Hello IPv6"
        assert summary["payload_length"] == 10
        assert summary["next_header"] == "UDP (17)"
        assert summary["hop_limit"] == 64

    def test_to_dict(self):
        """Test to_dict full serialization."""
        pkt = create_ipv6_packet(
            source_address="2001:db8:1::10",
            destination_address="2001:db8:4::20",
            payload="Hello IPv6",
            next_header="UDP",
            hop_limit=64,
        )
        data = pkt.to_dict()

        assert data["version"] == 6
        assert data["total_packet_size_bytes"] == 50  # 40 bytes header + 10 bytes payload
        assert data["source_address"] == "2001:db8:1::10"
        assert data["destination_address"] == "2001:db8:4::20"
        assert data["next_header_number"] == 17
        assert data["next_header_name"] == "UDP"
