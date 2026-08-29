"""
IPv6 Packet Processing Simulator - Core Package.

Phase 1: IPv6 Addressing & Project Foundation.
Phase 2: IPv6 Packet & Header Simulation.
Phase 3: Simulated Routers & IPv6 Routing Tables.
Phase 4: IPv6 Packet Forwarding Simulation.
Phase 5: Interactive Network Visualization & Simulation Dashboard.
Phase 6: Final Integration & Polish.
"""

from src.ipv6_address import (
    IPv6AddressAnalyzer,
    IPv6AnalysisResult,
    analyze_ipv6,
    validate_ipv6,
)
from src.ipv6_packet import (
    IPv6Packet,
    NextHeaderProtocol,
    create_ipv6_packet,
)
from src.routing_table import (
    Route,
    RoutingTable,
)
from src.router import (
    Router,
    RouterInterface,
)
from src.host import (
    Host,
    Link,
)
from src.network import (
    NetworkTopology,
    build_sample_topology,
)
from src.forwarding import (
    ForwardingResult,
    ForwardingStatus,
    ForwardingStep,
    PacketForwarder,
    forward_packet,
)
from src.visualization import (
    NetworkVisualizer,
)

__all__ = [
    "IPv6AddressAnalyzer",
    "IPv6AnalysisResult",
    "analyze_ipv6",
    "validate_ipv6",
    "IPv6Packet",
    "NextHeaderProtocol",
    "create_ipv6_packet",
    "Route",
    "RoutingTable",
    "Router",
    "RouterInterface",
    "Host",
    "Link",
    "NetworkTopology",
    "build_sample_topology",
    "ForwardingResult",
    "ForwardingStatus",
    "ForwardingStep",
    "PacketForwarder",
    "forward_packet",
    "NetworkVisualizer",
]
