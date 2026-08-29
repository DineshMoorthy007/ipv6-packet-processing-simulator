# IPv6 Packet Processing Simulator

An educational and modular network simulator designed to demonstrate IPv6 address mechanics, packet header structures, extension headers, and hop-by-hop packet processing.

---

## Phase 1: IPv6 Addressing & Project Foundation

### Objective
The goal of **Phase 1** is to establish the core project structure and implement the IPv6 addressing module. It allows users to parse, validate, expand, compress, classify, and analyze IPv6 addresses and subnet prefixes.

> [!NOTE]
> Packet forwarding, routing tables, and IPv6 header simulation are part of subsequent phases and are **not** included in Phase 1. Streamlit web UI integration will also be introduced in later phases.

---

## Technologies Used
- **Language**: Python 3.10+
- **Standard Library**: `ipaddress` (built-in module for robust IPv6 parsing and network calculations)
- **Testing**: `pytest`

---

## Current Features (Phase 1)
- **Address Validation**: Validates plain IPv6 addresses (`2001:db8::1`) and CIDR interface/network notations (`2001:db8::1/64`) with detailed error messages.
- **Representations**:
  - RFC 5952 standard compressed format (e.g. `2001:db8:1::10`)
  - Full 8-group expanded/exploded format (e.g. `2001:0db8:0001:0000:0000:0000:0000:0010`)
  - 128-bit confirmation, integer, hex, and binary representations
- **Address Classification**:
  - Global Unicast (`2000::/3`)
  - Link-Local Unicast (`fe80::/10`)
  - Unique Local / Private (`fc00::/7`)
  - Loopback (`::1`)
  - Unspecified (`::`)
  - Multicast (`ff00::/8`) with scope detection (Node-Local, Link-Local, Site-Local, Global)
  - Documentation prefix (`2001:db8::/32`)
- **Prefix & Subnet Analysis**:
  - Network address calculation
  - Prefix length extraction
  - Subnet netmask and hostmask
  - Interface Identifier (IID) / Host portion breakdown
  - Subnet total address capacity (e.g., $2^{64}$)
- **Interactive CLI & Direct Command Mode**: Terminal utility with interactive menu, direct address argument support, and built-in showcase demos.

---

## Project Structure

```text
ipv6-packet-processing-simulator/
│
├── src/
│   ├── __init__.py            # Package initializer & exports
│   └── ipv6_address.py        # Core IPv6 address analysis module
│
├── tests/
│   └── test_ipv6_address.py   # Comprehensive pytest test suite (44 test cases)
│
├── app.py                     # Command-line interface & demonstration app
├── requirements.txt           # Project dependencies (pytest)
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

### 1. Interactive Mode
Run `app.py` without arguments to access the interactive CLI menu:
```bash
python app.py
```

### 2. Direct Address Analysis
Pass an IPv6 address directly as a command-line argument:
```bash
python app.py 2001:db8:1::10
```

**Sample Output:**
```text
## IPv6 Address Analysis

Input Address : 2001:db8:1::10
Valid IPv6    : Yes
Compressed    : 2001:db8:1::10
Expanded      : 2001:0db8:0001:0000:0000:0000:0000:0010
Address Type  : Global/Documentation
Bit Length    : 128
```

### 3. Subnet / CIDR Analysis
Pass an IPv6 address with a prefix length:
```bash
python app.py 2001:db8:1::10/64
```

**Sample Output:**
```text
## IPv6 Address Analysis

Input Address : 2001:db8:1::10/64
Valid IPv6    : Yes
Compressed    : 2001:db8:1::10
Expanded      : 2001:0db8:0001:0000:0000:0000:0000:0010
Address Type  : Global/Documentation
Bit Length    : 128

--- Network / Subnet Details ---
Network       : 2001:db8:1::/64
Prefix Length : 64
Network Addr  : 2001:db8:1::
Netmask       : ffff:ffff:ffff:ffff::
Host Portion  : ::10
Interface ID  : 0000:0000:0000:0010
Total Hosts   : 2^64 (18,446,744,073,709,551,616 addresses)
```

### 4. Run Built-in Showcase Demo
```bash
python app.py --demo
```

---

## Running Tests

Execute the automated test suite with `pytest`:
```bash
pytest tests/ -v
```

All 44 test cases validate address validity, compression, expansion, subnet calculations, classifications, error handling, and serialization.

---

## Next Steps (Upcoming Phases)
- **Phase 2**: IPv6 Packet Header Modeling (Base 40-byte header, Hop Limit, Next Header, Flow Label, Traffic Class).
- **Phase 3**: IPv6 Extension Headers (Hop-by-Hop Options, Routing Header, Fragment Header, etc.).
- **Phase 4**: Router Node Simulation & Next-hop Routing / Forwarding Table Lookups.
- **Phase 5**: Interactive Streamlit Web UI & Visualization.
