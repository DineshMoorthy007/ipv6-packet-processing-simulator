# IPv6 Packet Processing Simulator

An educational and modular network simulator designed to demonstrate IPv6 address mechanics, packet header structures, extension headers, router architectures, routing tables, and hop-by-hop packet processing.

---

## Project Phases Overview

- **Phase 1 (Completed)**: IPv6 Addressing Engine & Project Foundation
- **Phase 2 (Completed)**: IPv6 Packet & Fixed 40-Byte Header Simulation
- **Phase 3 (Completed)**: Simulated Routers, IPv6 Interfaces, Routing Tables & Longest Prefix Match (LPM)
- **Phase 4 (Upcoming)**: End-to-End Hop-by-Hop Packet Forwarding Engine & Routing Simulation
- **Phase 5 (Upcoming)**: Interactive Streamlit Web UI & Real-Time Path Visualization

> [!NOTE]
> Packet forwarding, Hop Limit decrementing across hops, and transmission along the path are part of **Phase 4**. Phase 3 models routers, interface binding, connected/static routes, and next-hop decision making via Longest Prefix Match (LPM).

---

## Technologies Used
- **Language**: Python 3.10+
- **Standard Library**: `ipaddress` (built-in module for robust IPv6 parsing, subnet matching, and routing)
- **Testing**: `pytest`

---

## Simulated Network Architecture (Phase 3)

```text
  [Host A] (2001:db8:1::10/64)  -- Gateway: 2001:db8:1::1
     |
   (Subnet: 2001:db8:1::/64)
     |
  [Router R1]
     +-- eth0: 2001:db8:1::1/64   [Connected: 2001:db8:1::/64 -> Direct]
     +-- eth1: 2001:db8:2::1/64   [Connected: 2001:db8:2::/64 -> Direct]
     |                            [Static:    2001:db8:3::/64 -> 2001:db8:2::2]
     |                            [Static:    2001:db8:4::/64 -> 2001:db8:2::2]
   (Subnet: 2001:db8:2::/64)
     |
  [Router R2]
     +-- eth0: 2001:db8:2::2/64   [Connected: 2001:db8:2::/64 -> Direct]
     +-- eth1: 2001:db8:3::1/64   [Connected: 2001:db8:3::/64 -> Direct]
     |                            [Static:    2001:db8:1::/64 -> 2001:db8:2::1]
     |                            [Static:    2001:db8:4::/64 -> 2001:db8:3::2]
   (Subnet: 2001:db8:3::/64)
     |
  [Router R3]
     +-- eth0: 2001:db8:3::2/64   [Connected: 2001:db8:3::/64 -> Direct]
     +-- eth1: 2001:db8:4::1/64   [Connected: 2001:db8:4::/64 -> Direct]
     |                            [Static:    2001:db8:1::/64 -> 2001:db8:3::1]
     |                            [Static:    2001:db8:2::/64 -> 2001:db8:3::1]
   (Subnet: 2001:db8:4::/64)
     |
  [Host B] (2001:db8:4::20/64)  -- Gateway: 2001:db8:4::1
```

---

## Features

### Phase 1: IPv6 Addressing Module
- **Address Validation**: Validates standard IPv6 addresses and CIDR notations with clear error diagnostics.
- **Representations**: RFC 5952 compressed format, full 8-group expanded format, 128-bit confirmation, integer, hex, and binary strings.
- **Address Classification**: Global Unicast, Link-Local, Unique Local (Private), Loopback, Unspecified, Multicast (with scope detection), and Documentation prefixes.
- **Prefix & Subnet Analysis**: Network address, prefix length, netmask, hostmask, 64-bit Interface Identifier (IID), and subnet address capacity.

### Phase 2: IPv6 Packet & Header Simulation
- **Fixed 40-Byte Base Header Simulation**: Version (6), Traffic Class (0-255), Flow Label (0-1048575), byte-accurate Payload Length calculation, Next Header protocol resolution (`UDP`, `TCP`, `ICMPv6`, `No Next Header`), and Hop Limit (0-255).
- **Inspection & Summaries**: Clean terminal visualization (`display_header()`), serialization (`to_dict()`), and forwarding summary generator (`get_summary()`).

### Phase 3: Simulated Routers & Routing Tables
- **Routing Table Engine (`RoutingTable`)**:
  - Supports **Connected** routes (metric 0, direct delivery) and **Static** routes (configurable next-hop IP and metric).
  - Validation of destination network prefixes and next-hop IPv6 addresses.
  - Formatted ASCII routing table inspection.
- **Longest Prefix Match (LPM)**:
  - Efficiently evaluates candidate routes for a given destination address.
  - Automatically selects the route with the most specific (longest) prefix length (e.g. `/64` over `/48` over `/32`).
  - Gracefully reports "No Route to Host" for unreachable destinations.
- **Router Entity (`Router` & `RouterInterface`)**:
  - Models router nodes with multiple named IPv6 interfaces.
  - **Automatic Connected Route Generation**: Adding an interface automatically registers its directly connected subnet in the routing table.
  - Removing an interface automatically purges corresponding routes.
  - Route lookup utility returning matched prefix, selected route, next hop, outgoing interface, and route type.
- **Network Topology (`NetworkTopology`)**:
  - Models hosts, routers, and inter-device subnet links.
  - Built-in factory `build_sample_topology()` creating a 3-router linear topology with end-to-end static routing configured.

---

## Project Structure

```text
ipv6-packet-processing-simulator/
│
├── src/
│   ├── __init__.py            # Package exports
│   ├── ipv6_address.py        # Core IPv6 address analysis module (Phase 1)
│   ├── ipv6_packet.py         # IPv6 packet & header simulation module (Phase 2)
│   ├── routing_table.py       # Route & RoutingTable with LPM lookup (Phase 3)
│   ├── router.py              # Router & RouterInterface management (Phase 3)
│   └── network.py             # NetworkTopology, Host, Link, & Sample Topology (Phase 3)
│
├── tests/
│   ├── test_ipv6_address.py   # Address module unit tests (44 tests)
│   ├── test_ipv6_packet.py    # Packet & header unit tests (42 tests)
│   ├── test_routing_table.py  # Routing table & LPM unit tests (12 tests)
│   └── test_router.py         # Router, interfaces & network topology tests (11 tests)
│
├── app.py                     # Interactive CLI application & demonstration suite
├── requirements.txt           # Test dependencies (pytest)
├── README.md                  # Project documentation
└── .gitignore                 # Standard Python gitignore rules
```

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DineshMoorthy007/ipv6-packet-processing-simulator.git
   cd ipv6-packet-processing-simulator
   ```

2. **Install requirements** (for testing):
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Interactive CLI Menu
Run `app.py` without arguments:
```bash
python app.py
```
**Menu Options**:
1. Analyze an IPv6 Address or Subnet (Phase 1)
2. Create & Simulate an IPv6 Packet (Phase 2)
3. Simulated Routers & IPv6 Routing Tables (Phase 3)
4. Run Built-in Showcase Demonstrations (Phase 1, 2, & 3)
5. Exit

### 2. Display Network Topology
```bash
python app.py topology
```

### 3. Perform Route Lookup on a Router
```bash
python app.py route R1 2001:db8:4::20
```

**Output:**
```text
ROUTE LOOKUP
========================================

Router:
R1

Destination:
2001:db8:4::20

Matching Prefix:
2001:db8:4::/64

Selected Route:
2001:db8:4::/64

Next Hop:
2001:db8:2::2

Interface:
eth1

Route Type:
Static
========================================
```

### 4. Create Simulated IPv6 Packet (Phase 2)
```bash
python app.py packet 2001:db8:1::10 2001:db8:4::20 "Hello IPv6" UDP 64
```

### 5. Direct Address Analysis (Phase 1)
```bash
python app.py 2001:db8:1::10/64
```

### 6. Run Complete Showcase Demo
```bash
python app.py --demo
```

---

## Running Automated Tests

Run the comprehensive test suite with `pytest`:
```bash
pytest tests/ -v
```

**Test Breakdown**:
- `test_ipv6_address.py`: 44 passed
- `test_ipv6_packet.py`: 42 passed
- `test_routing_table.py`: 12 passed
- `test_router.py`: 11 passed
- **Total: 109 tests passed (0.28s)**

---

## Roadmap (Next Phases)
- **Phase 4**: End-to-End Hop-by-Hop Packet Forwarding Engine (Hop Limit decrementing, Router traversal, Next-Hop Resolution, Path Tracing).
- **Phase 5**: Interactive Streamlit Web Application with dynamic visual graph animations.
