# IPv6 Packet Processing Simulator

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-132%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An educational and modular network simulator designed to demonstrate IPv6 address mechanics, fixed 40-byte packet headers, multi-interface router architectures, Longest Prefix Match (LPM) routing tables, hop-by-hop packet forwarding, and interactive visual dashboards.

---

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Simulated Network Topology](#simulated-network-topology)
- [Core Features](#core-features)
- [How Packet Forwarding Works](#how-packet-forwarding-works)
- [Standardized Test Scenarios](#standardized-test-scenarios)
- [Installation & Setup](#installation--setup)
- [Usage & Execution](#usage--execution)
  - [Interactive Dashboard](#1-interactive-dashboard)
  - [Standalone Lab Demonstration](#2-standalone-laboratory-demo)
  - [CLI Direct Commands](#3-cli-direct-commands)
- [Running Automated Tests](#running-automated-tests)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Project Overview

The **IPv6 Packet Processing Simulator** models the lifecycle of IPv6 network packets without requiring administrative OS permissions, raw sockets, or third-party packet capturers. It provides a pure, deterministic simulation engine that illustrates:

1. **IPv6 Addressing**: RFC 5952 compression, 8-group expansion, classification, and CIDR subnet math.
2. **Base Header Modeling**: 40-byte fixed header construction, byte-accurate payload length calculation, and Next Header multiplexing.
3. **Router Mechanics**: Multi-interface virtual routers with automatic connected route registration.
4. **Longest Prefix Match (LPM)**: Resolving overlapping routing table entries (`/64` vs `/48` vs `/32`).
5. **Hop-by-Hop Forwarding**: Default gateway dispatch, Hop Limit checking & decrementing, next-hop resolution, direct subnet delivery, and drop detection.
6. **Visual Inspection**: ASCII topology graphs, device specification cards, step-by-step movement snapshots, and execution event timelines.

---

## System Architecture

```text
User Input / CLI / Demo Script
              ↓
  [IPv6 Address Analyzer]   --> Validates & Expands IPv6 Addresses
              ↓
  [IPv6 Packet Generator]   --> Builds 40-Byte Base Header (Version=6, Hop Limit, Next Header)
              ↓
     [Source Host]          --> Selects Default Gateway Router Interface
              ↓
    [Router Traversal]      --> Evaluates Destination IP via Routing Table
              ↓
  [Longest Prefix Match]    --> Selects Most Specific Prefix Route
              ↓
  [Hop Limit Processing]    --> Drops if Hop Limit <= 1, else Decrements (HL = HL - 1)
              ↓
     [Next Router]          --> Continues Traversal across Links
              ↓
  [Destination Delivery]    --> Successfully Delivered to Destination Host (or Dropped)
              ↓
  [Visual Dashboard]        --> Renders ASCII Diagram, Movement Snapshots, Timeline, Stats
```

---

## Simulated Network Topology

```text
  [Host A] (2001:db8:1::10/64)  -- Default Gateway: 2001:db8:1::1
     |
   (Subnet: 2001:db8:1::/64)
     |
  [Router R1]
     +-- eth0: 2001:db8:1::1/64   [Connected: 2001:db8:1::/64 -> Direct]
     +-- eth1: 2001:db8:2::1/64   [Connected: 2001:db8:2::/64 -> Direct]
     |                            [Static:    2001:db8:3::/64 -> 2001:db8:2::2 via eth1]
     |                            [Static:    2001:db8:4::/64 -> 2001:db8:2::2 via eth1]
   (Subnet: 2001:db8:2::/64)
     |
  [Router R2]
     +-- eth0: 2001:db8:2::2/64   [Connected: 2001:db8:2::/64 -> Direct]
     +-- eth1: 2001:db8:3::1/64   [Connected: 2001:db8:3::/64 -> Direct]
     |                            [Static:    2001:db8:1::/64 -> 2001:db8:2::1 via eth0]
     |                            [Static:    2001:db8:4::/64 -> 2001:db8:3::2 via eth1]
   (Subnet: 2001:db8:3::/64)
     |
  [Router R3]
     +-- eth0: 2001:db8:3::2/64   [Connected: 2001:db8:3::/64 -> Direct]
     +-- eth1: 2001:db8:4::1/64   [Connected: 2001:db8:4::/64 -> Direct]
     |                            [Static:    2001:db8:1::/64 -> 2001:db8:3::1 via eth0]
     |                            [Static:    2001:db8:2::/64 -> 2001:db8:3::1 via eth0]
   (Subnet: 2001:db8:4::/64)
     |
  [Host B] (2001:db8:4::20/64)  -- Default Gateway: 2001:db8:4::1
```

---

## Core Features

- **IPv6 Address Validation & Canonical Formatting**:
  - Full RFC 5952 recommendation formatting (zero-compression `::`, lowercase hex).
  - 8-group full 128-bit expansion, binary representation, and integer conversions.
  - Comprehensive classification: Global Unicast, Link-Local (`fe80::/10`), Unique-Local (`fc00::/7`), Loopback (`::1`), Unspecified (`::`), Multicast (`ff00::/8`) with scope detection, and Documentation (`2001:db8::/32`).
  - CIDR subnet breakdown: Netmask, hostmask, 64-bit Interface Identifier (IID), total usable address space ($2^{128-\text{prefix}}$).

- **Fixed 40-Byte IPv6 Header Simulation**:
  - Version: `6`
  - Traffic Class: `0-255`
  - Flow Label: `0-1048575`
  - Payload Length: Dynamic byte-accurate calculation
  - Next Header: `UDP` (`17`), `TCP` (`6`), `ICMPv6` (`58`), `No Next Header` (`59`)
  - Hop Limit: `0-255` (default: `64`)

- **Router & Routing Engine**:
  - Multi-interface management (`eth0`, `eth1`).
  - Automatic `Connected` route creation upon interface binding.
  - Static route table configuration.
  - **Longest Prefix Match (LPM)** lookup algorithm.

- **Hop-by-Hop Forwarding Engine**:
  - Hop Limit validation and decrementing ($64 \to 63 \to 62 \dots$).
  - Automatic packet drop on Hop Limit expiration (`DROPPED_HOP_LIMIT`).
  - Automatic packet drop on routing failure (`DROPPED_NO_ROUTE`).
  - Preservation of original packet fields throughout transmission.

- **Visual Dashboard & Presentation**:
  - ASCII network architecture diagrams with highlighted active paths (`[* Host A *] -> ...`).
  - Device inspection cards for Hosts and Routers.
  - Step-by-step sequential packet movement snapshots.
  - Visual packet processing event timelines (`[OK]`, `[X]`).
  - Summary statistics tables.

---

## How Packet Forwarding Works

```text
1. Packet Created at Host A (Hop Limit: 64)
2. Host A determines destination is remote -> Forwards to default gateway R1
3. R1 receives packet:
   - Verifies Hop Limit > 1
   - Performs LPM lookup for 2001:db8:4::20 -> Selects 2001:db8:4::/64 (Next Hop: 2001:db8:2::2 on eth1)
   - Decrements Hop Limit: 64 -> 63
   - Forwards to R2 via Subnet 2001:db8:2::/64
4. R2 receives packet:
   - Verifies Hop Limit > 1
   - Performs LPM lookup -> Selects 2001:db8:4::/64 (Next Hop: 2001:db8:3::2 on eth1)
   - Decrements Hop Limit: 63 -> 62
   - Forwards to R3 via Subnet 2001:db8:3::/64
5. R3 receives packet:
   - Identifies 2001:db8:4::/64 as directly connected on eth1
   - Decrements Hop Limit: 62 -> 61
   - Delivers packet to Host B
6. Forwarding Status: DELIVERED (Final Hop Limit: 61, Routers Traversed: 3)
```

---

## Standardized Test Scenarios

The simulator includes 5 built-in educational test scenarios:

| # | Scenario | Source | Destination | Initial HL | Expected Status | Routers | Final HL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Multi-Hop Delivery | `2001:db8:1::10` | `2001:db8:4::20` | `64` | `DELIVERED` | `R1, R2, R3` | `61` |
| **2** | Hop Limit Expiration | `2001:db8:1::10` | `2001:db8:4::20` | `1` | `DROPPED_HOP_LIMIT` | `R1` | `1` |
| **3** | No Route to Host | `2001:db8:1::10` | `2001:db8:99::10` | `64` | `DROPPED_NO_ROUTE` | `R1` | `63` |
| **4** | Longest Prefix Match | `2001:db8:0::10` | `2001:db8:4:10::20` | `64` | `SUCCESS` (LPM `/64`) | `R_LPM` | `63` |
| **5** | Direct Subnet Delivery | `2001:db8:1::10` | `2001:db8:1::25` | `64` | `DELIVERED` | None (0) | `64` |

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DineshMoorthy007/ipv6-packet-processing-simulator.git
   cd ipv6-packet-processing-simulator
   ```

2. **Set up a Python Virtual Environment** (Python 3.10+):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install test dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage & Execution

### 1. Interactive Dashboard
Launch the unified interactive simulator menu:
```bash
python app.py
```
```text
======================================================================
             IPv6 PACKET PROCESSING SIMULATOR
 Educational Computer Networks Laboratory Simulation Dashboard
======================================================================
Main Menu:
  [1] IPv6 Address Analyzer (Phase 1)
  [2] IPv6 Packet Simulator (Phase 2)
  [3] Network Topology & Device Inspector (Phase 3 & 5)
  [4] Routing Tables & LPM Inspector (Phase 3 & 5)
  [5] Packet Forwarding Simulation (Phase 4 & 5)
  [6] Predefined Test Scenarios Runner (Phase 6)
  [7] Complete Showcase Demonstration (Phases 1 - 6)
  [8] Exit
```

### 2. Standalone Laboratory Demo
Run the zero-input demonstration script:
```bash
python demo.py
```

### 3. CLI Direct Commands

- **Forwarding Simulation**:
  ```bash
  python app.py forward "Host A" "Host B" "Hello IPv6" 64
  ```
- **Inspect Device Specifications**:
  ```bash
  python app.py device "Host A"
  python app.py device "R1"
  ```
- **Analyze IPv6 Address or Subnet**:
  ```bash
  python app.py 2001:db8:1::10/64
  ```
- **Perform Route Lookup**:
  ```bash
  python app.py route R1 2001:db8:4::20
  ```
- **Run Complete Showcase**:
  ```bash
  python app.py --demo
  ```

---

## Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest tests/ -v
```

### Test Suite Breakdown
| Test File | Focus Area | Tests | Status |
| :--- | :--- | :--- | :--- |
| `tests/test_ipv6_address.py` | Addressing, validation, classification, subnet math | 44 | **Passed** |
| `tests/test_ipv6_packet.py` | 40-byte base header, field validation, payload sizing | 42 | **Passed** |
| `tests/test_routing_table.py` | Route entries, routing tables, LPM resolution | 12 | **Passed** |
| `tests/test_router.py` | Multi-interface router, topology connectivity | 11 | **Passed** |
| `tests/test_forwarding.py` | Hop-by-hop forwarding engine, field immutability | 8 | **Passed** |
| `tests/test_visualization.py` | Graphs, device cards, timelines, statistics | 10 | **Passed** |
| `tests/test_scenarios.py` | Standardized educational scenarios (1 - 5) | 5 | **Passed** |
| **Total** | **Comprehensive Test Suite** | **132** | **100% Passed** |

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

## Project Structure

```text
ipv6-packet-processing-simulator/
│
├── src/
│   ├── __init__.py            # Package exports
│   ├── ipv6_address.py        # Core IPv6 address analysis module
│   ├── ipv6_packet.py         # IPv6 packet & 40-byte base header simulation
│   ├── routing_table.py       # RoutingTable with Longest Prefix Match (LPM)
│   ├── router.py              # Router & RouterInterface management
│   ├── host.py                # Host & Link definitions
│   ├── network.py             # NetworkTopology & reference topology builder
│   ├── forwarding.py          # Hop-by-hop packet forwarding engine
│   └── visualization.py       # Visual diagrams, timelines, device cards & dashboard
│
├── tests/
│   ├── test_ipv6_address.py   # Address module unit tests (44 tests)
│   ├── test_ipv6_packet.py    # Packet & header unit tests (42 tests)
│   ├── test_routing_table.py  # Routing table & LPM unit tests (12 tests)
│   ├── test_router.py         # Router, interfaces & network tests (11 tests)
│   ├── test_forwarding.py     # End-to-end packet forwarding tests (8 tests)
│   ├── test_visualization.py  # Visualization & dashboard tests (10 tests)
│   └── test_scenarios.py      # Standardized scenario tests (5 tests)
│
├── docs/
│   ├── architecture.md        # Technical architecture & data flow specification
│   └── test-scenarios.md      # Detailed scenario specifications & test logs
│
├── screenshots/
│   └── .gitkeep               # Directory for visual documentation assets
│
├── app.py                     # Interactive CLI dashboard & demonstration suite
├── demo.py                    # Standalone zero-input laboratory demonstration script
├── requirements.txt           # Test dependencies (pytest)
├── README.md                  # Comprehensive project documentation
├── LICENSE                    # MIT open-source license
└── .gitignore                 # Standard Python gitignore rules
```

---

## Future Enhancements

- **Interactive Streamlit Web Dashboard**: Visual browser GUI with animated packet transit graphs, interactive sliders for Hop Limits, and topology builders.
- **IPv6 Extension Headers**: Hop-by-Hop Options (`0`), Routing Header (`43`), and Fragmentation (`44`).
- **ICMPv6 Simulation**: Time Exceeded (`Type 3 / Code 0`) and Destination Unreachable (`Type 1 / Code 0`) packet generation.
- **Neighbor Discovery Protocol (NDP)**: Router Advertisement (RA), Router Solicitation (RS), and Neighbor Solicitation (NS).

---

## License

This project is open-source software licensed under the terms of the [MIT License](LICENSE).
