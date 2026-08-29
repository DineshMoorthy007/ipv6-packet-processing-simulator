# IPv6 Packet Processing Simulator

An educational and modular network simulator designed to demonstrate IPv6 address mechanics, packet header structures, routing tables, Longest Prefix Match (LPM), hop-by-hop packet forwarding, and interactive visual dashboards.

---

## Project Phases Overview

- **Phase 1 (Completed)**: IPv6 Addressing Engine & Project Foundation
- **Phase 2 (Completed)**: IPv6 Packet & Fixed 40-Byte Header Simulation
- **Phase 3 (Completed)**: Simulated Routers, Interfaces, Routing Tables & Longest Prefix Match (LPM)
- **Phase 4 (Completed)**: End-to-End Hop-by-Hop Packet Forwarding Engine & Routing Simulation
- **Phase 5 (Completed)**: Interactive Network Visualization, Device Inspectors & Simulation Dashboard

---

## Technologies Used
- **Language**: Python 3.10+
- **Standard Library**: `ipaddress` (built-in module for robust IPv6 parsing, subnet calculations, and routing)
- **Testing**: `pytest`

---

## Simulated Network Architecture

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

### Phase 1: IPv6 Addressing Engine
- Address validation, RFC 5952 compression, 8-group expansion, 128-bit confirmation, integer, hex, and binary representations.
- Scope and type classification (Global Unicast, Link-Local, Unique-Local Private, Loopback, Unspecified, Multicast with scope detection, Documentation).
- Prefix and subnet breakdown (network address, netmask, hostmask, 64-bit Interface ID, subnet host capacity).

### Phase 2: IPv6 Packet & Header Simulation
- Fixed 40-byte base header modeling: Version (`6`), Traffic Class (`0-255`), Flow Label (`0-1048575`), byte-accurate Payload Length, Next Header (`UDP`, `TCP`, `ICMPv6`, `No Next Header`), and Hop Limit (`0-255`).
- Visual header inspector (`format_header_view()`) and summary serialization.

### Phase 3: Simulated Routers & Routing Tables
- `RoutingTable` engine with Connected and Static routes.
- **Longest Prefix Match (LPM)** resolving destination lookup across overlapping subnets.
- `Router` entity with interface binding and automated connected route registration.
- Multi-router linear `NetworkTopology` (`build_sample_topology()`).

### Phase 4: Packet Forwarding Engine
- **Hop-by-Hop Packet Forwarding**:
  1. Packet departure from source host via default gateway.
  2. Router receives packet and checks destination.
  3. **Direct Delivery**: If destination subnet is directly attached to the router, decrements Hop Limit and delivers packet.
  4. **Hop Limit Check & Decrement**: Drops packet with `DROPPED_HOP_LIMIT` if `Hop Limit <= 1`. Otherwise decrements Hop Limit ($64 \to 63 \to 62 \dots$).
  5. **Route Lookup**: Performs Longest Prefix Match (LPM) on current router's routing table.
  6. **Next Hop Resolution**: Resolves next router interface and continues traversal until destination is reached.
- **Forwarding Event Log**: Maintains a step-by-step sequential audit log of every routing decision and Hop Limit mutation.
- **Preservation of Packet Integrity**: All other packet fields remain intact throughout transmission.

### Phase 5: Visualization & Simulation Dashboard
- **Topology Visualization**: Visual diagram with dynamic path highlighting (`[* Host A *] -> [* R1 *] -> ...`).
- **Device Inspector Cards**: Comprehensive specifications for Hosts and Routers.
- **Step-by-Step Packet Movement Snapshots**: Visual hop-by-hop progression display.
- **Processing Timeline**: Vertical workflow timeline (`[OK]` steps, `[X]` drop indicators).
- **Forwarding Statistics**: Summary table of hop counts, status, and transit metrics.
- **Clean Architecture for Streamlit Integration**: Core logic is fully decoupled from the terminal interface.

---

## Project Structure

```text
ipv6-packet-processing-simulator/
│
├── src/
│   ├── __init__.py            # Package exports
│   ├── ipv6_address.py        # Core IPv6 address analysis module (Phase 1)
│   ├── ipv6_packet.py         # IPv6 packet & header simulation module (Phase 2)
│   ├── routing_table.py       # RoutingTable with LPM lookup (Phase 3)
│   ├── router.py              # Router & RouterInterface management (Phase 3)
│   ├── network.py             # NetworkTopology, Host, Link, & Sample Topology (Phase 3)
│   ├── forwarding.py          # Hop-by-hop packet forwarding engine (Phase 4)
│   └── visualization.py       # Visual graph, timeline, device cards & dashboard (Phase 5)
│
├── tests/
│   ├── test_ipv6_address.py   # Address module unit tests (44 tests)
│   ├── test_ipv6_packet.py    # Packet & header unit tests (42 tests)
│   ├── test_routing_table.py  # Routing table & LPM unit tests (12 tests)
│   ├── test_router.py         # Router, interfaces & network tests (11 tests)
│   ├── test_forwarding.py     # End-to-end packet forwarding tests (8 tests)
│   └── test_visualization.py  # Visualization & dashboard tests (10 tests)
│
├── app.py                     # Interactive CLI dashboard & demonstration suite
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

2. **Install dependencies** (for testing):
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Interactive Dashboard Menu
Run `app.py` without arguments:
```bash
python app.py
```
**Menu Options**:
1. IPv6 Address Analyzer (Phase 1)
2. IPv6 Packet / Header Simulator (Phase 2)
3. Network Topology & Device Inspector (Phase 3 & 5)
4. Router Routing Tables & LPM Inspector (Phase 3 & 5)
5. Packet Forwarding Simulation & Visual Dashboard (Phase 4 & 5)
6. Run Built-in Showcase Demonstrations (Phases 1 - 5)
7. Exit

### 2. Forward Packet from Host A to Host B (Visual Dashboard)
```bash
python app.py forward "Host A" "Host B" "Hello IPv6" 64
```

**Output:**
```text
==================================================
              IPv6 PACKET HEADER
==================================================
Version              : 6
Traffic Class        : 0
Flow Label           : 0
Payload Length       : 10 bytes
Next Header          : UDP (17)
Hop Limit            : 61

Source Address:
2001:db8:1::10

Destination Address:
2001:db8:4::20
==================================================
Payload Content:
Hello IPv6
==================================================

======================================================================
          TOPOLOGY VISUALIZATION: SAMPLE 3-ROUTER LINEAR NETWORK
======================================================================

Network Architecture Diagram:
----------------------------------------------------------------------
  +-----------+         +--------+         +--------+         +--------+         +-----------+
  |  [* Host A *] |---------|  [* R1 *] |---------|  [* R2 *] |---------|  [* R3 *] |---------|  [* Host B *] |
  +-----------+         +--------+         +--------+         +--------+         +-----------+
 2001:db8:1::/64     2001:db8:2::/64    2001:db8:3::/64    2001:db8:4::/64
----------------------------------------------------------------------

Active Forwarding Path:
  [Host A] -> [R1] -> [R2] -> [R3] -> [Host B]

Device Inventory:
  Hosts   : Host A, Host B
  Routers : R1, R2, R3
  Subnets : 4 configured links
======================================================================

PACKET PROCESSING TIMELINE
============================================================
  [OK] Packet created at Host A
        |
        v
  [OK] Packet received by R1
        |
        v
  [OK] R1 performing route lookup
        |
        v
  [OK] R1 selected route (Longest Prefix Match)
        |
        v
  [OK] R1 forwarding packet via eth1
        |
        v
  [OK] Packet received by R2
        |
        v
  [OK] R2 performing route lookup
        |
        v
  [OK] R2 selected route (Longest Prefix Match)
        |
        v
  [OK] R2 forwarding packet via eth1
        |
        v
  [OK] Packet received by R3
        |
        v
  [OK] Destination network is directly connected on R3 (eth1)
        |
        v
  [OK] Packet delivered to Host B
        |
        v
  [OK] PACKET DELIVERED SUCCESSFULLY
============================================================

Forwarding Statistics
---------------------------------------------
Status                 : DELIVERED
Reason / Details       : Packet delivered successfully
Initial Hop Limit      : 64
Final Hop Limit        : 61
Routers Traversed      : 3 (R1, R2, R3)
Total Event Steps      : 13
Source Address         : 2001:db8:1::10 (Host A)
Destination Address    : 2001:db8:4::20 (Host B)
---------------------------------------------
```

### 3. Inspect Device Cards
```bash
python app.py device "Host A"
python app.py device "R1"
```

### 4. Direct Route Lookup
```bash
python app.py route R1 2001:db8:4::20
```

### 5. Run Full Demonstration Showcase
```bash
python app.py --demo
```

---

## Screenshots

```text
screenshots/
├── address-analysis.png
├── ipv6-header.png
├── topology.png
├── routing-table.png
├── successful-forwarding.png
└── packet-drop.png
```

---

## Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest tests/ -v
```

**Test Suite Summary**:
- `test_ipv6_address.py`: 44 passed
- `test_ipv6_packet.py`: 42 passed
- `test_routing_table.py`: 12 passed
- `test_router.py`: 11 passed
- `test_forwarding.py`: 8 passed
- `test_visualization.py`: 10 passed
- **Total: 127 tests passed in 0.34s**
