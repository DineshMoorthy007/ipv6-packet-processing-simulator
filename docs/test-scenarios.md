# Standardized Test Scenarios - IPv6 Packet Processing Simulator

This document details the 5 standardized laboratory test scenarios, their configuration parameters, expected behaviors, and underlying computer networking concepts demonstrated.

---

## Summary Table

| Scenario # | Title | Source | Destination | Initial Hop Limit | Expected Outcome | Routers Traversed | Final Hop Limit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Scenario 1** | Successful Multi-Hop Delivery | `2001:db8:1::10` | `2001:db8:4::20` | `64` | `DELIVERED` | `R1, R2, R3` (3) | `61` |
| **Scenario 2** | Hop Limit Expiration Drop | `2001:db8:1::10` | `2001:db8:4::20` | `1` | `DROPPED_HOP_LIMIT` | `R1` (1) | `1` |
| **Scenario 3** | No Route to Host Drop | `2001:db8:1::10` | `2001:db8:99::10` | `64` | `DROPPED_NO_ROUTE` | `R1` (1) | `63` |
| **Scenario 4** | Longest Prefix Match (LPM) | `2001:db8:0::10` | `2001:db8:4:10::20` | `64` | `SUCCESS` (LPM /64) | `R_LPM` (1) | `63` |
| **Scenario 5** | Direct Subnet Delivery | `2001:db8:1::10` | `2001:db8:1::25` | `64` | `DELIVERED` | None (0) | `64` |

---

## Detailed Scenarios

### Scenario 1 — Successful Multi-Hop Delivery
- **Concept Demonstrated**: Multi-hop routing, hop limit decrement, packet header preservation, static route chaining.
- **Topology**: `Host A` $\leftrightarrow$ `R1` $\leftrightarrow$ `R2` $\leftrightarrow$ `R3` $\leftrightarrow$ `Host B`.
- **Packet Input**:
  - Source: `2001:db8:1::10` (Host A)
  - Destination: `2001:db8:4::20` (Host B)
  - Payload: `"Hello IPv6"`
  - Next Header: `UDP` (`17`)
  - Initial Hop Limit: `64`
- **Hop-by-Hop Trace**:
  1. `Host A`: Packet created, egresses via default gateway (`2001:db8:1::1`).
  2. `R1`: Receives packet (HL=64). Route lookup matches `2001:db8:4::/64` $\to$ Next Hop: `2001:db8:2::2` (`eth1`). Decrements HL $64 \to 63$.
  3. `R2`: Receives packet (HL=63). Route lookup matches `2001:db8:4::/64` $\to$ Next Hop: `2001:db8:3::2` (`eth1`). Decrements HL $63 \to 62$.
  4. `R3`: Receives packet (HL=62). Destination is directly connected on `eth1`. Decrements HL $62 \to 61$. Delivers to `Host B`.
- **Expected Status**: `DELIVERED` (Final HL: `61`).

---

### Scenario 2 — Hop Limit Expiration Drop
- **Concept Demonstrated**: Loop prevention, TTL/Hop Limit expiration, packet dropping.
- **Packet Input**:
  - Source: `2001:db8:1::10`
  - Destination: `2001:db8:4::20`
  - Initial Hop Limit: `1`
- **Hop-by-Hop Trace**:
  1. `Host A`: Packet created with Hop Limit = 1.
  2. `R1`: Receives packet. Router checks `Hop Limit <= 1`. Hop limit expired!
  3. Packet is dropped at `R1`.
- **Expected Status**: `DROPPED_HOP_LIMIT` (Reason: `"Hop Limit expired at router"`).

---

### Scenario 3 — No Route to Host Drop
- **Concept Demonstrated**: Unroutable destination networks, routing table lookup misses.
- **Packet Input**:
  - Source: `2001:db8:1::10`
  - Destination: `2001:db8:99::10` (Unreachable network)
  - Initial Hop Limit: `64`
- **Hop-by-Hop Trace**:
  1. `Host A`: Packet created and sent to default gateway `R1`.
  2. `R1`: Receives packet, decrements HL $64 \to 63$. Performs routing table lookup for `2001:db8:99::10`.
  3. No route matches in `R1`'s routing table. Packet is dropped.
- **Expected Status**: `DROPPED_NO_ROUTE` (Reason: `"No matching route found in routing table of R1"`).

---

### Scenario 4 — Longest Prefix Match (LPM) Selection
- **Concept Demonstrated**: Subnet mask specificity, CIDR longest prefix matching.
- **Router Configuration**:
  - Route A: `2001:db8::/32` $\to$ Next Hop: `2001:db8:10::1` (`eth0`)
  - Route B: `2001:db8:4::/48` $\to$ Next Hop: `2001:db8:10::2` (`eth1`)
  - Route C: `2001:db8:4:10::/64` $\to$ Next Hop: `2001:db8:10::3` (`eth2`)
- **Query Destination**: `2001:db8:4:10::20`
- **Evaluation**: All 3 routes encompass this IP address, but Route C (`/64`) has the longest prefix length.
- **Expected Selected Route**: `2001:db8:4:10::/64` via `2001:db8:10::3` (`eth2`).

---

### Scenario 5 — Directly Connected Subnet Delivery
- **Concept Demonstrated**: Local link broadcast/delivery without traversing intermediate routers.
- **Packet Input**:
  - Source: `2001:db8:1::10` (Host A, Subnet: `2001:db8:1::/64`)
  - Destination: `2001:db8:1::25` (Local host on same `/64` subnet)
  - Initial Hop Limit: `64`
- **Evaluation**: Destination is on the local subnet. Delivered directly without router hops.
- **Expected Status**: `DELIVERED` (Router Hops: `0`, Final HL: `64`).
