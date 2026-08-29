# IPv6 Packet Processing Simulator

An educational and modular network simulator designed to demonstrate IPv6 address mechanics, packet header structures, routing tables, Longest Prefix Match (LPM), and hop-by-hop packet forwarding.

---

## Project Phases Overview

- **Phase 1 (Completed)**: IPv6 Addressing Engine & Project Foundation
- **Phase 2 (Completed)**: IPv6 Packet & Fixed 40-Byte Header Simulation
- **Phase 3 (Completed)**: Simulated Routers, Interfaces, Routing Tables & Longest Prefix Match (LPM)
- **Phase 4 (Completed)**: End-to-End Hop-by-Hop Packet Forwarding Engine & Routing Simulation
- **Phase 5 (Upcoming)**: Interactive Streamlit Web UI & Real-Time Graph Animation

---

## Technologies Used
- **Language**: Python 3.10+
- **Standard Library**: `ipaddress` (built-in module for robust IPv6 parsing, subnetting, and route calculations)
- **Testing**: `pytest`

---

## Simulated Network Topology

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
- Address validation, RFC 5952 compression, 8-group expansion, 128-bit confirmation, integer, hex, and binary representation.
- Address classification (Global Unicast, Link-Local, Unique-Local, Loopback, Unspecified, Multicast with scope detection, Documentation).
- Prefix and subnet calculation (network address, netmask, hostmask, interface ID, subnet capacity).

### Phase 2: IPv6 Packet & Header Simulation
- Fixed 40-byte base header modeling: Version (`6`), Traffic Class (`0-255`), Flow Label (`0-1048575`), byte-accurate Payload Length, Next Header (`UDP`, `TCP`, `ICMPv6`, `No Next Header`), and Hop Limit (`0-255`).
- Textual packet display (`display_header()`) and summary serialization.

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
- **Preservation of Packet Integrity**: All other packet fields (Version, Traffic Class, Flow Label, Payload Length, Next Header, Source Address, Destination Address, Payload) remain completely intact throughout transmission.

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
│   └── forwarding.py          # Hop-by-hop packet forwarding engine (Phase 4)
│
├── tests/
│   ├── test_ipv6_address.py   # Address module unit tests (44 tests)
│   ├── test_ipv6_packet.py    # Packet & header unit tests (42 tests)
│   ├── test_routing_table.py  # Routing table & LPM unit tests (12 tests)
│   ├── test_router.py         # Router, interfaces & network tests (11 tests)
│   └── test_forwarding.py     # End-to-end packet forwarding tests (8 tests)
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

2. **Install dependencies** (for running test suites):
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
4. IPv6 Packet Forwarding Simulation (Phase 4)
5. Run Built-in Showcase Demonstrations (Phases 1 - 4)
6. Exit

### 2. Forward Packet from Host A to Host B (Phase 4)
```bash
python app.py forward "Host A" "Host B" "Hello IPv6" 64
```

**Output:**
```text
============================================================
             IPv6 PACKET FORWARDING SIMULATION
============================================================

Packet Information:
------------------------------------------------------------
Source Address      : 2001:db8:1::10 (Host A)
Destination Address : 2001:db8:4::20 (Host B)
Payload             : Hello IPv6
Payload Length      : 10 bytes
Next Header         : UDP (17)
Initial Hop Limit   : 64

Forwarding Path:
------------------------------------------------------------
  Host A
    |
    v
  R1
    |
    v
  R2
    |
    v
  R3
    |
    v
  Host B

Forwarding Result:
------------------------------------------------------------
Status              : DELIVERED
Reason / Details    : Packet delivered successfully
Initial Hop Limit   : 64
Final Hop Limit     : 61
Routers Traversed   : 3 (R1, R2, R3)

============================================================
                 DETAILED FORWARDING EVENT LOG
============================================================
[1] Packet created at Host A
    Source      : 2001:db8:1::10
    Destination : 2001:db8:4::20
    Hop Limit   : 64
[2] Packet received by R1
    Hop Limit   : 64
[3] R1 performing route lookup
    Destination : 2001:db8:4::20
[4] R1 selected route (Longest Prefix Match)
    Prefix      : 2001:db8:4::/64
    Next Hop    : 2001:db8:2::2
    Interface   : eth1
[5] R1 forwarding packet via eth1
    Hop Limit   : 64 -> 63
[6] Packet received by R2
    Hop Limit   : 63
[7] R2 performing route lookup
    Destination : 2001:db8:4::20
[8] R2 selected route (Longest Prefix Match)
    Prefix      : 2001:db8:4::/64
    Next Hop    : 2001:db8:3::2
    Interface   : eth1
[9] R2 forwarding packet via eth1
    Hop Limit   : 63 -> 62
[10] Packet received by R3
    Hop Limit   : 62
[11] Destination network is directly connected on R3 (eth1)
    Hop Limit   : 62 -> 61
[12] Packet delivered to Host B
[13] PACKET DELIVERED SUCCESSFULLY
============================================================
```

### 3. Test Hop Limit Expiration Drop
```bash
python app.py forward "Host A" "Host B" "Hello IPv6" 1
```

**Output Status:** `DROPPED_HOP_LIMIT` (Reason: Hop Limit expired at router R1).

### 4. Test No-Route Drop
```bash
python app.py forward "Host A" "2001:db8:99::10" "Test" 64
```

**Output Status:** `DROPPED_NO_ROUTE` (Reason: No matching route found in routing table of R1).

### 5. Run Full Demonstration Showcase
```bash
python app.py --demo
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
- **Total: 117 tests passed in 0.28s**

---

## Roadmap (Phase 5)
- **Phase 5**: Interactive Streamlit Web Application featuring dynamic network topology visualization, packet creation controls, hop-by-hop animation, and real-time header inspection.
