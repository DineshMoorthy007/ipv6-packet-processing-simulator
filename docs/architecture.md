# System Architecture - IPv6 Packet Processing Simulator

## Overview

The **IPv6 Packet Processing Simulator** is a modular Python-based educational simulation framework designed to model core IPv6 networking operations without requiring physical network interfaces or raw OS sockets.

---

## High-Level Architecture

```text
+-----------------------------------------------------------------------------------+
|                                 USER INTERFACE                                    |
|   Interactive Terminal CLI (app.py) | Standalone Demo (demo.py) | Test Suite      |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             CORE SIMULATION MODULES                               |
|                                                                                   |
|  +---------------------+   +---------------------+   +--------------------------+  |
|  |     Addressing      |   |    Packet Header    |   |     Routing Tables       |  |
|  | (ipv6_address.py)   |-->|  (ipv6_packet.py)   |-->|   (routing_table.py)     |  |
|  | - RFC 5952 Compress |   | - Fixed 40B Header  |   | - Longest Prefix Match   |  |
|  | - 8-Group Exploded  |   | - Dynamic Payload B |   | - Connected & Static Rts |  |
|  | - Scope / Subnet    |   | - Protocol Resolve  |   | - Table ASCII Formatter  |  |
|  +---------------------+   +---------------------+   +--------------------------+  |
|                                                              |                    |
|                                                              v                    |
|  +---------------------+   +---------------------+   +--------------------------+  |
|  |    Visualization    |   |  Forwarding Engine  |   |   Routers & Topology     |  |
|  | (visualization.py)  |<--|  (forwarding.py)    |<--|   (router.py / host.py   |  |
|  | - ASCII Diagrams    |   | - Hop-by-Hop Trace  |   |    / network.py)         |  |
|  | - Timeline / Stats  |   | - Hop Limit Mutate  |   | - Multi-Interface Router |  |
|  | - Graph Data Export |   | - Drop Handling     |   | - 3-Router Linear Topo   |  |
|  +---------------------+   +---------------------+   +--------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## Core Module Descriptions

### 1. `src/ipv6_address.py`
- **Class**: `IPv6AddressAnalyzer`, `IPv6AnalysisResult`
- **Functions**: `validate_ipv6(addr)`, `analyze_ipv6(addr)`
- **Key Functions**: Validates standard addresses and CIDR notations, performs RFC 5952 compression, 8-group expansion, classification (Global, Link-Local, Unique-Local, Loopback, Unspecified, Multicast with scope detection, Documentation), and extracts prefix lengths, netmasks, hostmasks, and 64-bit Interface Identifiers (IID).

### 2. `src/ipv6_packet.py`
- **Class**: `IPv6Packet`, `NextHeaderProtocol`
- **Function**: `create_ipv6_packet(src, dst, payload, proto, hop_limit)`
- **Key Functions**: Represents the fixed 40-byte IPv6 base header:
  - Version: `6` (strictly validated)
  - Traffic Class: `0–255` (8 bits)
  - Flow Label: `0–1048575` (20 bits)
  - Payload Length: Calculated in bytes from UTF-8 strings or raw bytes
  - Next Header: Resolves names (`UDP`, `TCP`, `ICMPv6`, `No Next Header`) and numbers (`17`, `6`, `58`, `59`)
  - Hop Limit: `0–255` (default: 64)
  - Source & Destination: Validated using the addressing module

### 3. `src/routing_table.py`
- **Class**: `Route`, `RoutingTable`
- **Key Functions**: Manages route entries (`Connected` vs `Static`), validates destination network prefixes, and implements **Longest Prefix Match (LPM)** to select the most specific route when overlapping subnets match a destination.

### 4. `src/router.py` & `src/host.py`
- **Class**: `Router`, `RouterInterface`, `Host`, `Link`
- **Key Functions**:
  - `Router`: Manages multiple named IPv6 interfaces (`eth0`, `eth1`). Adding an interface automatically generates a `Connected` route in the router's routing table.
  - `Router.lookup_route(dest_ip)`: Evaluates destination address against the routing table via LPM.
  - `Host`: Models end-devices with assigned IPv6 address and default gateway router.

### 5. `src/network.py`
- **Class**: `NetworkTopology`
- **Function**: `build_sample_topology()`
- **Key Functions**: Models interconnections and builds the reference 3-router multi-hop linear network (`Host A -> R1 -> R2 -> R3 -> Host B`).

### 6. `src/forwarding.py`
- **Class**: `PacketForwarder`, `ForwardingResult`, `ForwardingStep`, `ForwardingStatus`
- **Function**: `forward_packet(packet, topology, source_host_name)`
- **Key Functions**: Executes hop-by-hop packet forwarding:
  1. Checks whether destination is directly connected to the current router.
  2. Enforces Hop Limit checks (drops packet if `Hop Limit <= 1`).
  3. Decrements Hop Limit ($64 \to 63 \to 62 \dots$).
  4. Performs route lookup via LPM.
  5. Resolves next router by next-hop IP in the topology and continues traversal until delivery.
  6. Preserves immutability of all other packet header fields.

### 7. `src/visualization.py`
- **Class**: `NetworkVisualizer`
- **Key Functions**: Provides formatted ASCII network diagrams with dynamic path highlighting, device inspector cards, step-by-step movement snapshots, processing event timelines, and summary statistics.

---

## Data Flow & Processing Lifecycle

```text
1. Address Input
   "2001:db8:1::10" ──> [IPv6AddressAnalyzer] ──> Validation & Canonical Representation

2. Packet Creation
   (Src, Dst, Payload, UDP, 64) ──> [IPv6Packet] ──> Fixed 40-Byte Header Construction

3. Forwarding Initiation
   [Host A] ──> Finds default gateway (2001:db8:1::1) ──> Transmits to Router R1

4. Router Processing Loop (at R1, R2, R3)
   ├── A. Destination directly connected? ──> (YES) ──> Decrement Hop Limit ──> Deliver to Host B
   ├── B. Hop Limit <= 1? ──────────────────> (YES) ──> DROP (DROPPED_HOP_LIMIT)
   ├── C. Decrement Hop Limit ($HL = HL - 1$)
   ├── D. Routing Table LPM Lookup ─────────> (NO ROUTE) ──> DROP (DROPPED_NO_ROUTE)
   └── E. Resolve next router by next-hop IP ──> Forward to next Router

5. Reporting & Visualization
   [ForwardingResult] ──> [NetworkVisualizer] ──> Header View, Path Diagram, Movement Snapshots, Timeline, Stats
```
