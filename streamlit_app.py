"""
IPv6 Packet Processing Simulator - Professional Streamlit Web Dashboard

An interactive, laboratory-grade web application for simulating IPv6 addressing,
40-byte base header structures, router interfaces, routing tables, Longest Prefix Match (LPM),
hop-by-hop packet forwarding, and standardized test scenarios.
"""

from __future__ import annotations

import streamlit as st
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6
from src.ipv6_packet import IPv6Packet, create_ipv6_packet
from src.router import Router
from src.host import Host, Link
from src.network import NetworkTopology, build_sample_topology
from src.forwarding import ForwardingResult, ForwardingStatus, PacketForwarder, forward_packet
from src.visualization import NetworkVisualizer


# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Modern Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPv6 Packet Processing Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Sleek Modern UI with Clean Spacing & Typography
st.markdown(
    """
    <style>
    /* Global Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Headings: Clean, Spacious, and Uncrowded */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: #f8fafc !important;
    }

    h2 {
        font-size: 1.75rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3, .stSubheader {
        font-size: 1.25rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        color: #e2e8f0 !important;
    }

    h4 {
        font-size: 1.05rem !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.5rem !important;
        color: #cbd5e1 !important;
    }

    /* Sidebar Clean Dark Palette */
    [data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }

    /* Hide the radio button group label */
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }

    /* Full-width, clean vertical navigation list */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
        width: 100% !important;
    }

    /* Hide the circular radio bullseye/dot completely */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Uniform full-width modern pill item */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 11px 16px !important;
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        background-color: rgba(30, 41, 59, 0.4) !important;
        color: #94a3b8 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
    }

    /* Sleek hover state */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(51, 65, 85, 0.6) !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
        transform: translateX(2px);
    }

    /* Active / Selected Tab State with clean background highlight */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: rgba(14, 165, 233, 0.12) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-left: 4px solid #0284c7 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.15) !important;
    }

    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 700;
        font-size: 1.35rem !important;
    }

    /* Professional Status Badges */
    .status-badge-delivered {
        display: inline-block;
        padding: 8px 16px;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }

    .status-badge-dropped {
        display: inline-block;
        padding: 8px 16px;
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid #ef4444;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }

    .status-badge-info {
        display: inline-block;
        padding: 6px 12px;
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid #3b82f6;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
    }

    /* Code Block Styling */
    .stCodeBlock {
        border: 1px solid #334155;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Cached / Stateful Topology Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def get_default_topology() -> NetworkTopology:
    """Instantiate and cache the reference 3-router linear network topology."""
    return build_sample_topology()


topology = get_default_topology()


# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style='padding: 6px 0 12px 0;'>
        <div style='font-size: 1.2rem; font-weight: 700; color: #f8fafc;'>IPv6 Simulator</div>
        <div style='font-size: 0.8rem; color: #64748b; margin-top: 2px;'>Computer Networks Laboratory</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("<hr style='border: none; border-top: 1px solid #1e293b; margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

nav_options = [
    "Dashboard",
    "IPv6 Address Analyzer",
    "IPv6 Packet Simulator",
    "Network Topology",
    "Routing Tables & LPM",
    "Packet Forwarding Engine",
    "Test Scenarios",
]

page = st.sidebar.radio("Navigation Menu", nav_options, index=0)

st.sidebar.markdown("<hr style='border: none; border-top: 1px solid #1e293b; margin: 16px 0;'>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div style='background-color: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #1e293b;'>
        <div style='font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;'>Reference Topology</div>
        <div style='font-size: 0.84rem; color: #94a3b8; margin-top: 4px; font-family: monospace;'>
            Host A &rarr; R1 &rarr; R2 &rarr; R3 &rarr; Host B
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 1. Dashboard Page
# =============================================================================
if page == "Dashboard":
    st.subheader("IPv6 Packet Processing Simulator")
    st.markdown(
        "A modular, deterministic simulation framework demonstrating IPv6 address parsing, "
        "40-byte fixed base headers, multi-interface routing, **Longest Prefix Match (LPM)**, "
        "and hop-by-hop packet forwarding."
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 16px 0;'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div style='background:#1e293b; padding:18px; border-radius:10px; border:1px solid #334155; height:100%;'>
                <h4 style='color:#38bdf8; margin-top:0; margin-bottom:12px;'>1. IPv6 Addressing</h4>
                <ul style='color:#cbd5e1; font-size:0.9rem; margin-bottom:0; line-height:1.6;'>
                    <li>RFC 5952 Canonical Compression</li>
                    <li>Full 8-Group 128-Bit Expansion</li>
                    <li>Unicast, Link-Local & Multicast Scopes</li>
                    <li>Subnet Analysis & 64-bit Interface IDs</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div style='background:#1e293b; padding:18px; border-radius:10px; border:1px solid #334155; height:100%;'>
                <h4 style='color:#38bdf8; margin-top:0; margin-bottom:12px;'>2. Packet Headers & Routing</h4>
                <ul style='color:#cbd5e1; font-size:0.9rem; margin-bottom:0; line-height:1.6;'>
                    <li>Fixed 40-Byte Base Header Model</li>
                    <li>Traffic Class & Flow Label Control</li>
                    <li>Multi-Interface Router Entities</li>
                    <li>Longest Prefix Match (LPM) Engine</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div style='background:#1e293b; padding:18px; border-radius:10px; border:1px solid #334155; height:100%;'>
                <h4 style='color:#38bdf8; margin-top:0; margin-bottom:12px;'>3. Forwarding & Inspection</h4>
                <ul style='color:#cbd5e1; font-size:0.9rem; margin-bottom:0; line-height:1.6;'>
                    <li>Hop Limit Validation & Decrements</li>
                    <li>Drop Reasons (Hop Limit / No Route)</li>
                    <li>Sequential Node Movement Snapshots</li>
                    <li>Forwarding Event Timelines & Metrics</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

    st.subheader("Simulated 3-Router Linear Network Architecture")
    st.code(
        NetworkVisualizer.format_topology_graph(topology),
        language="text",
    )

    st.subheader("End-to-End Simulation Workflow")
    st.markdown(
        """
        ```text
        IPv6 Address ──> 40-Byte Header ──> Source Host ──> Gateway Router (R1) ──> LPM Route Lookup ──>
        Hop Limit Decrement (64 -> 63) ──> Next Hop (R2) ──> Next Hop (R3) ──> Destination Host (DELIVERED)
        ```
        """
    )


# =============================================================================
# 2. IPv6 Address Analyzer Page
# =============================================================================
elif page == "IPv6 Address Analyzer":
    st.subheader("IPv6 Address Analyzer")
    st.markdown("Validate and analyze IPv6 addresses, CIDR prefix lengths, canonical formats, and subnet allocations.")

    col1, col2 = st.columns([3, 1])
    with col1:
        addr_input = st.text_input(
            "Enter IPv6 Address or CIDR Subnet:",
            value="2001:db8:1::10/64",
            help="Examples: 2001:db8:1::10/64, fe80::1, ::1, ff02::1, fd12:3456:789a:1::1/64",
        )
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("Analyze Address", type="primary", use_container_width=True)

    if addr_input or analyze_btn:
        result = analyze_ipv6(addr_input.strip())

        if not result.is_valid:
            st.error(f"Invalid IPv6 Address / Subnet: {result.error_message}")
        else:
            st.success("Valid IPv6 Address")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Address Scope / Type", result.address_type or "Unknown")
            m2.metric("Total Bit Length", f"{result.bit_length} bits")
            m3.metric("Prefix Length", f"/{result.prefix_length}" if result.prefix_length is not None else "None")
            m4.metric(
                "Subnet Hosts",
                f"2^{128 - result.prefix_length}" if result.prefix_length is not None else "1 host",
            )

            st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Representation Formats")
                st.markdown("**RFC 5952 Compressed Canonical:**")
                st.code(result.compressed or "N/A", language="text")

                st.markdown("**Full 8-Group Expanded:**")
                st.code(result.expanded or "N/A", language="text")

                st.markdown("**Hexadecimal Value:**")
                st.code(result.hex_value or "N/A", language="text")

                st.markdown("**Binary Representation:**")
                st.code(result.binary_representation or "N/A", language="text")

            with col_b:
                st.subheader("Network & Subnet Breakdown")
                if result.has_prefix:
                    st.markdown(f"**Network Address:** `{result.network_address}`")
                    st.markdown(f"**Netmask:** `{result.netmask}`")
                    st.markdown(f"**Hostmask:** `{result.hostmask}`")
                    st.markdown(f"**Interface Identifier (IID):** `{result.interface_identifier or 'N/A'}`")
                    if result.total_addresses is not None:
                        st.markdown(f"**Total Subnet Addresses:** `{result.total_addresses:,}`")
                else:
                    st.markdown("**Host Address (No CIDR subnet prefix supplied)**")
                    st.markdown(f"**Compressed Format:** `{result.compressed}`")
                    st.markdown(f"**Integer Value:** `{result.integer_value}`")

            with st.expander("View Formatted Terminal Report"):
                st.code(IPv6AddressAnalyzer.format_report(result), language="text")


# =============================================================================
# 3. IPv6 Packet Simulator Page
# =============================================================================
elif page == "IPv6 Packet Simulator":
    st.subheader("IPv6 Packet & Base Header Simulator")
    st.markdown("Construct simulated IPv6 packets with fixed 40-byte base headers and dynamic payload sizing.")

    col1, col2 = st.columns(2)
    with col1:
        src_ip = st.text_input("Source IPv6 Address:", value="2001:db8:1::10")
        dst_ip = st.text_input("Destination IPv6 Address:", value="2001:db8:4::20")
        payload = st.text_area("Payload Data:", value="Hello IPv6 Network Simulation", height=100)

    with col2:
        proto = st.selectbox(
            "Next Header Protocol:",
            ["UDP (17)", "TCP (6)", "ICMPv6 (58)", "No Next Header (59)"],
            index=0,
        )
        proto_name = proto.split()[0]

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            tc = st.number_input("Traffic Class (0-255):", min_value=0, max_value=255, value=0)
            hl = st.slider("Hop Limit (0-255):", min_value=0, max_value=255, value=64)
        with col_sub2:
            fl = st.number_input("Flow Label (0-1048575):", min_value=0, max_value=1048575, value=0)

    create_pkt_btn = st.button("Create Simulated IPv6 Packet", type="primary")

    if create_pkt_btn or "last_created_packet" in st.session_state:
        try:
            if create_pkt_btn:
                pkt = create_ipv6_packet(
                    source_address=src_ip.strip(),
                    destination_address=dst_ip.strip(),
                    payload=payload,
                    traffic_class=int(tc),
                    flow_label=int(fl),
                    next_header=proto_name,
                    hop_limit=int(hl),
                )
                st.session_state["last_created_packet"] = pkt
            else:
                pkt = st.session_state["last_created_packet"]

            st.success("IPv6 Packet Created Successfully")

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("IP Version", f"v{pkt.version}")
            p2.metric("Base Header Size", "40 Bytes (Fixed)")
            p3.metric("Payload Length", f"{pkt.payload_length} Bytes")
            p4.metric("Total Packet Size", f"{40 + pkt.payload_length} Bytes")

            st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.subheader("40-Byte Base Header Breakdown")
                header_data = [
                    {"Header Field": "Version", "Size / Bits": "4 bits", "Value": str(pkt.version)},
                    {"Header Field": "Traffic Class", "Size / Bits": "8 bits", "Value": str(pkt.traffic_class)},
                    {"Header Field": "Flow Label", "Size / Bits": "20 bits", "Value": str(pkt.flow_label)},
                    {"Header Field": "Payload Length", "Size / Bits": "16 bits", "Value": f"{pkt.payload_length} bytes"},
                    {"Header Field": "Next Header", "Size / Bits": "8 bits", "Value": f"{pkt.next_header_name} ({pkt.next_header})"},
                    {"Header Field": "Hop Limit", "Size / Bits": "8 bits", "Value": str(pkt.hop_limit)},
                    {"Header Field": "Source Address", "Size / Bits": "128 bits", "Value": pkt.source_address},
                    {"Header Field": "Destination Address", "Size / Bits": "128 bits", "Value": pkt.destination_address},
                ]
                st.dataframe(header_data, use_container_width=True, hide_index=True)

            with col_h2:
                st.subheader("Payload Content Inspection")
                st.code(pkt.payload if pkt.payload else "<Empty Payload>", language="text")

                st.subheader("Structured Terminal Header")
                st.code(NetworkVisualizer.format_header_view(pkt), language="text")

        except ValueError as err:
            st.error(f"Packet Creation Error: {err}")


# =============================================================================
# 4. Network Topology Page
# =============================================================================
elif page == "Network Topology":
    st.subheader("Network Topology & Device Inspector")
    st.markdown("Explore the simulated 3-router linear network, configured interfaces, and subnet links.")

    st.subheader("Topology Architecture Diagram")
    st.code(NetworkVisualizer.format_topology_graph(topology), language="text")

    st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

    st.subheader("Inspect Device Specification Card")
    all_devs = list(topology.hosts.keys()) + list(topology.routers.keys())
    selected_dev = st.selectbox("Select Device to Inspect:", all_devs, index=0)

    if selected_dev:
        st.code(NetworkVisualizer.format_device_details(selected_dev, topology), language="text")

    st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

    st.subheader("Configured Subnet Links")
    links_data = []
    for link in topology.links:
        links_data.append({
            "Node A": f"{link.node_a} ({link.interface_a})",
            "Node B": f"{link.node_b} ({link.interface_b})",
            "Subnet Network": link.network,
        })
    st.dataframe(links_data, use_container_width=True, hide_index=True)


# =============================================================================
# 5. Routing Tables & LPM Page
# =============================================================================
elif page == "Routing Tables & LPM":
    st.subheader("Router Routing Tables & Longest Prefix Match (LPM)")
    st.markdown("Inspect router interfaces, active routing tables, and test Longest Prefix Match (LPM) route lookups.")

    selected_router_name = st.selectbox("Select Router:", list(topology.routers.keys()), index=0)
    router = topology.get_router(selected_router_name)

    if router:
        col_r1, col_r2 = st.columns([1, 1])

        with col_r1:
            st.subheader(f"Interfaces on {router.name}")
            intf_data = []
            for intf in router.interfaces.values():
                intf_data.append({
                    "Interface": intf.name,
                    "IPv6 Address": f"{intf.ip_address}/{intf.prefix_length}",
                    "Subnet": intf.network,
                    "Status": "UP" if intf.is_up else "DOWN",
                })
            st.dataframe(intf_data, use_container_width=True, hide_index=True)

        with col_r2:
            st.subheader(f"Active Routing Table ({router.name})")
            routes_data = router.routing_table.to_list()
            st.dataframe(routes_data, use_container_width=True, hide_index=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

        st.subheader("Route Lookup & Longest Prefix Match Query")
        query_dest = st.text_input(
            f"Enter Destination IPv6 to Lookup on {router.name}:",
            value="2001:db8:4::20",
            help="Example: 2001:db8:4::20 (Host B) or 2001:db8:1::10 (Host A)",
        )

        if st.button("Lookup Route", type="primary"):
            lookup = router.lookup_route(query_dest.strip())

            if lookup["status"] == "SUCCESS":
                st.markdown(
                    f"<div class='status-badge-info'>Route Match: {lookup['route_type']}</div>",
                    unsafe_allow_html=True,
                )
                st.write("")

                l1, l2, l3 = st.columns(3)
                l1.metric("Best Matching Prefix (LPM)", lookup["selected_prefix"])
                l2.metric("Next Hop IPv6", lookup["next_hop"])
                l3.metric("Outgoing Interface", lookup["interface"])

                if len(lookup["matching_prefixes"]) > 1:
                    st.info(f"Longest Prefix Match: Evaluated candidate prefixes {lookup['matching_prefixes']} and selected most specific prefix {lookup['selected_prefix']}.")
            else:
                st.error(f"Lookup Failed: {lookup['message']}")


# =============================================================================
# 6. Packet Forwarding Simulation Page
# =============================================================================
elif page == "Packet Forwarding Engine":
    st.subheader("Packet Forwarding Simulation Cockpit")
    st.markdown("Simulate end-to-end hop-by-hop packet transit across routers `R1 -> R2 -> R3` with real-time Hop Limit updates.")

    col1, col2 = st.columns(2)
    with col1:
        src_selection = st.selectbox("Select Source Host:", ["Host A (2001:db8:1::10)", "Host B (2001:db8:4::20)"], index=0)
        src_name = "Host A" if "Host A" in src_selection else "Host B"
        src_ip_val = topology.get_host(src_name).ipv6_address

        dst_mode = st.radio("Destination Mode:", ["Predefined Host", "Custom IPv6 Address"], horizontal=True)
        if dst_mode == "Predefined Host":
            dst_selection = st.selectbox("Select Destination Host:", ["Host B (2001:db8:4::20)", "Host A (2001:db8:1::10)"], index=0)
            dst_name = "Host B" if "Host B" in dst_selection else "Host A"
            dst_ip_val = topology.get_host(dst_name).ipv6_address
        else:
            dst_ip_val = st.text_input("Enter Custom Destination IPv6 Address:", value="2001:db8:99::10")
            dst_name = None

        payload_txt = st.text_input("Payload Content:", value="Hello IPv6 Simulation")

    with col2:
        proto_choice = st.selectbox("Next Header Protocol:", ["UDP", "TCP", "ICMPv6"], index=0)
        hl_val = st.slider("Initial Hop Limit:", min_value=1, max_value=128, value=64, help="Set to 1 to test Hop Limit Expiration Drop!")

        st.markdown(
            """
            <div style='background:#1e293b; padding:14px; border-radius:8px; border:1px solid #334155; font-size:0.86rem; color:#cbd5e1; line-height:1.6;'>
                <strong>Forwarding Protocol Mechanics:</strong><br>
                &bull; Each router decrements Hop Limit (HL = HL - 1).<br>
                &bull; Dropped if HL &le; 1 upon arrival at intermediate router.<br>
                &bull; Router applies Longest Prefix Match to forward to next hop.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    start_sim_btn = st.button("Start Forwarding Simulation", type="primary", use_container_width=True)

    if start_sim_btn or "last_forwarding_result" in st.session_state:
        try:
            if start_sim_btn:
                sim_pkt = create_ipv6_packet(
                    source_address=src_ip_val,
                    destination_address=dst_ip_val.strip(),
                    payload=payload_txt,
                    next_header=proto_choice,
                    hop_limit=hl_val,
                )
                sim_res = forward_packet(
                    packet=sim_pkt,
                    topology=topology,
                    source_host_name=src_name,
                )
                st.session_state["last_forwarding_packet"] = sim_pkt
                st.session_state["last_forwarding_result"] = sim_res
            else:
                sim_pkt = st.session_state["last_forwarding_packet"]
                sim_res = st.session_state["last_forwarding_result"]

            st.markdown("<hr style='border: none; border-top: 1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)

            # Result Header Badge
            if sim_res.status == ForwardingStatus.DELIVERED:
                st.markdown(
                    f"<div class='status-badge-delivered'>STATUS: PACKET DELIVERED SUCCESSFULLY</div>",
                    unsafe_allow_html=True,
                )
            elif sim_res.status == ForwardingStatus.DROPPED_HOP_LIMIT:
                st.markdown(
                    f"<div class='status-badge-dropped'>STATUS: PACKET DROPPED (Hop Limit Expired)</div>",
                    unsafe_allow_html=True,
                )
            elif sim_res.status == ForwardingStatus.DROPPED_NO_ROUTE:
                st.markdown(
                    f"<div class='status-badge-dropped'>STATUS: PACKET DROPPED (No Matching Route)</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='status-badge-info'>STATUS: {sim_res.status.value}</div>",
                    unsafe_allow_html=True,
                )

            st.write("")

            # Top Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Initial Hop Limit", sim_res.initial_hop_limit)
            m2.metric("Final Hop Limit", sim_res.final_hop_limit)
            m3.metric("Routers Traversed", sim_res.num_router_hops)
            m4.metric("Forwarding Event Steps", len(sim_res.log))

            st.markdown(f"**Forwarding Path:** `{' -> '.join(sim_res.path)}`")

            # Visual Tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "Active Path Diagram",
                "Processing Timeline",
                "Step-by-Step Snapshots",
                "Header Integrity Check",
            ])

            with tab1:
                st.subheader("Network Architecture with Active Path Highlight")
                st.code(NetworkVisualizer.format_topology_graph(topology, active_path=sim_res.path), language="text")

            with tab2:
                st.subheader("Packet Processing Event Timeline")
                st.code(NetworkVisualizer.format_forwarding_timeline(sim_res), language="text")

            with tab3:
                st.subheader("Step-by-Step Packet Movement Snapshots")
                snapshots = NetworkVisualizer.format_packet_movement_steps(sim_res)
                for snap in snapshots:
                    st.text(snap)
                    st.markdown("---")

            with tab4:
                st.subheader("Packet Header Integrity Inspection")
                st.markdown(
                    "Observe that **only Hop Limit** is mutated during router forwarding. "
                    "All other fields remain intact."
                )
                col_hdr1, col_hdr2 = st.columns(2)
                with col_hdr1:
                    st.markdown("##### Transmitted Packet Header")
                    st.code(NetworkVisualizer.format_header_view(sim_pkt), language="text")
                with col_hdr2:
                    st.markdown("##### Forwarding Summary & Statistics")
                    st.code(NetworkVisualizer.format_forwarding_stats(sim_res), language="text")

        except ValueError as err:
            st.error(f"Forwarding Execution Error: {err}")


# =============================================================================
# 7. Test Scenarios Page
# =============================================================================
elif page == "Test Scenarios":
    st.subheader("Standardized Laboratory Test Scenarios")
    st.markdown("Execute pre-configured test scenarios to demonstrate fundamental IPv6 networking concepts.")

    scenario_options = [
        "Scenario 1: Successful Multi-Hop Delivery (Host A -> Host B)",
        "Scenario 2: Hop Limit Expiration Packet Drop (Hop Limit = 1)",
        "Scenario 3: No Route to Destination Drop (2001:db8:99::10)",
        "Scenario 4: Longest Prefix Match (LPM) Selection (/64 over /48 and /32)",
        "Scenario 5: Directly Connected Subnet Delivery (Local Subnet)",
        "Run All 5 Standard Scenarios Sequentially",
    ]

    chosen_sc = st.selectbox("Select Scenario to Execute:", scenario_options, index=0)

    if st.button("Execute Selected Scenario", type="primary"):
        if "Scenario 1" in chosen_sc:
            st.subheader("Scenario 1: Successful Multi-Hop Delivery")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 1 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.markdown("<div class='status-badge-delivered'>DELIVERED: Host A -> R1 -> R2 -> R3 -> Host B</div>", unsafe_allow_html=True)
            st.write("")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Scenario 2" in chosen_sc:
            st.subheader("Scenario 2: Hop Limit Expiration Packet Drop")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 2 Test", hop_limit=1)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.markdown("<div class='status-badge-dropped'>DROPPED_HOP_LIMIT: Dropped at R1 (Hop Limit = 1 <= 1)</div>", unsafe_allow_html=True)
            st.write("")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Scenario 3" in chosen_sc:
            st.subheader("Scenario 3: No Route to Destination Drop")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:99::10", payload="Scenario 3 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.markdown("<div class='status-badge-dropped'>DROPPED_NO_ROUTE: Dropped at R1 (No matching route for 2001:db8:99::10)</div>", unsafe_allow_html=True)
            st.write("")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Scenario 4" in chosen_sc:
            st.subheader("Scenario 4: Longest Prefix Match (LPM) Demonstration")
            demo_router = Router("DemoRouter")
            demo_router.add_interface("eth0", "2001:db8:0::1/32")
            demo_router.add_interface("eth1", "2001:db8:4::1/48")
            demo_router.add_interface("eth2", "2001:db8:4:10::1/64")
            demo_router.add_static_route("2001:db8::/32", next_hop="2001:db8:10::1", interface="eth0")
            demo_router.add_static_route("2001:db8:4::/48", next_hop="2001:db8:10::2", interface="eth1")
            demo_router.add_static_route("2001:db8:4:10::/64", next_hop="2001:db8:10::3", interface="eth2")

            lookup = demo_router.lookup_route("2001:db8:4:10::20")
            st.markdown(
                f"<div class='status-badge-delivered'>LPM Selected: {lookup['selected_prefix']} via {lookup['next_hop']} ({lookup['interface']})</div>",
                unsafe_allow_html=True,
            )
            st.write("")
            st.code(demo_router.format_lookup_result(lookup), language="text")

        elif "Scenario 5" in chosen_sc:
            st.subheader("Scenario 5: Directly Connected Subnet Delivery")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:1::25", payload="Scenario 5 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.markdown("<div class='status-badge-delivered'>DIRECT DELIVERY: Delivered on local 2001:db8:1::/64 (0 router hops)</div>", unsafe_allow_html=True)
            st.write("")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Run All" in chosen_sc:
            st.subheader("Batch Results for Standard Scenarios")
            batch_results = []
            scenarios = [
                ("Scenario 1: Multi-Hop Delivery", "2001:db8:1::10", "2001:db8:4::20", 64),
                ("Scenario 2: Hop Limit Drop", "2001:db8:1::10", "2001:db8:4::20", 1),
                ("Scenario 3: No Route Drop", "2001:db8:1::10", "2001:db8:99::10", 64),
                ("Scenario 5: Direct Subnet", "2001:db8:1::10", "2001:db8:1::25", 64),
            ]
            for name, src, dst, hl in scenarios:
                p = create_ipv6_packet(src, dst, payload="Batch Test", hop_limit=hl)
                r = forward_packet(p, topology, source_host_name="Host A")
                batch_results.append({
                    "Scenario": name,
                    "Source": src,
                    "Destination": dst,
                    "Initial HL": hl,
                    "Final HL": r.final_hop_limit,
                    "Outcome": r.status.value,
                    "Path": " -> ".join(r.path),
                })
            st.dataframe(batch_results, use_container_width=True, hide_index=True)
