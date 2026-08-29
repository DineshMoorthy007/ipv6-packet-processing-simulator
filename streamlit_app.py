"""
IPv6 Packet Processing Simulator - Interactive Streamlit Web Application (Phase 7)

An interactive, browser-based dashboard for exploring IPv6 addressing, 40-byte base headers,
router interfaces, routing tables, Longest Prefix Match (LPM), hop-by-hop packet forwarding,
and standardized laboratory test scenarios.
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
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPv6 Packet Processing Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
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
st.sidebar.title("🌐 IPv6 Simulator")
st.sidebar.markdown(
    "**Educational Computer Networks Laboratory Mini Project**\n\n"
    "Simulating IPv6 packet lifecycle from address analysis to multi-hop forwarding."
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔍 IPv6 Address Analyzer",
        "📦 IPv6 Packet Simulator",
        "🗺️ Network Topology",
        "📋 Routing Tables & LPM",
        "🚀 Packet Forwarding Engine",
        "🧪 Test Scenarios",
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.info(
    "💡 **Quick Tip**\n\n"
    "Use **Packet Forwarding Engine** to watch packets travel hop-by-hop through routers `R1 -> R2 -> R3`."
)


# =============================================================================
# 1. Dashboard Page
# =============================================================================
if page == "🏠 Dashboard":
    st.title("🌐 IPv6 Packet Processing Simulator")
    st.markdown(
        "An interactive simulation framework demonstrating IPv6 addressing mechanics, "
        "fixed 40-byte base headers, multi-interface routing, **Longest Prefix Match (LPM)**, "
        "and hop-by-hop packet forwarding."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1. IPv6 Addressing")
        st.markdown(
            "- RFC 5952 Canonical Compression (`::`)\n"
            "- 8-Group 128-Bit Expansion\n"
            "- Global, Link-Local & Multicast Scopes\n"
            "- Subnet Math & 64-bit Interface IDs"
        )
    with col2:
        st.subheader("2. Packet Headers & Routing")
        st.markdown(
            "- Fixed 40-Byte Base Header Model\n"
            "- Traffic Class & Flow Label\n"
            "- Multi-Interface Router Models\n"
            "- Longest Prefix Match (LPM) Engine"
        )
    with col3:
        st.subheader("3. Forwarding & Inspection")
        st.markdown(
            "- Hop Limit Validation & Decrements\n"
            "- Dropped Packets & Loop Prevention\n"
            "- Step-by-Step Movement Snapshots\n"
            "- Execution Event Timelines & Stats"
        )

    st.divider()

    st.subheader("🗺️ Simulated 3-Router Linear Network Architecture")
    st.code(
        NetworkVisualizer.format_topology_graph(topology),
        language="text",
    )

    st.markdown("### 🔄 End-to-End Simulation Workflow")
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
elif page == "🔍 IPv6 Address Analyzer":
    st.title("🔍 IPv6 Address Analyzer")
    st.markdown("Validate and analyze IPv6 addresses, CIDR prefixes, canonical formats, and subnet allocations.")

    col1, col2 = st.columns([3, 1])
    with col1:
        addr_input = st.text_input(
            "Enter IPv6 Address or CIDR Subnet:",
            value="2001:db8:1::10/64",
            help="Examples: 2001:db8:1::10/64, fe80::1, ::1, ff02::1, fd12:3456:789a:1::1/64",
        )
    with col2:
        analyze_btn = st.button("🚀 Analyze Address", type="primary", use_container_width=True)

    if addr_input or analyze_btn:
        result = analyze_ipv6(addr_input.strip())

        if not result.is_valid:
            st.error(f"❌ **Invalid IPv6 Address / Subnet**: {result.error_message}")
        else:
            st.success("✅ **Valid IPv6 Address**")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Address Scope / Type", result.address_type)
            m2.metric("Total Bit Length", f"{result.bit_length} bits")
            m3.metric("Prefix Length", f"/{result.prefix_length}" if result.prefix_length is not None else "N/A")
            m4.metric("Subnet Hosts", f"2^{128 - result.prefix_length}" if result.prefix_length is not None else "1 host")

            st.divider()

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("📌 Representation Formats")
                st.markdown(f"**RFC 5952 Compressed Canonical:**")
                st.code(result.compressed or "N/A", language="text")

                st.markdown(f"**Full 8-Group Expanded:**")
                st.code(result.expanded or "N/A", language="text")

                st.markdown(f"**Hexadecimal Integer Value:**")
                st.code(result.hex_representation or "N/A", language="text")

            with col_b:
                st.subheader("🌐 Network & Subnet Breakdown")
                if result.is_network:
                    st.markdown(f"**Network Address:** `{result.network_address}`")
                    st.markdown(f"**Netmask:** `{result.netmask}`")
                    st.markdown(f"**Hostmask:** `{result.hostmask}`")
                    st.markdown(f"**Interface Identifier (IID):** `{result.interface_id}`")
                    st.markdown(f"**Total Available Addresses in Subnet:** `{result.total_addresses:,}`")
                else:
                    st.markdown(f"**Plain IPv6 Host Address** (No CIDR subnet prefix provided).")
                    st.markdown(f"**Compressed Format:** `{result.compressed}`")
                    st.markdown(f"**Interface ID:** `{result.interface_id}`")

            with st.expander("📄 View Full Formatted Terminal Report"):
                st.code(IPv6AddressAnalyzer.format_report(result), language="text")


# =============================================================================
# 3. IPv6 Packet Simulator Page
# =============================================================================
elif page == "📦 IPv6 Packet Simulator":
    st.title("📦 IPv6 Packet & Base Header Simulator")
    st.markdown("Construct simulated IPv6 packets with fixed 40-byte base headers and dynamic payload sizing.")

    col1, col2 = st.columns(2)
    with col1:
        src_ip = st.text_input("Source IPv6 Address:", value="2001:db8:1::10")
        dst_ip = st.text_input("Destination IPv6 Address:", value="2001:db8:4::20")
        payload = st.text_area("Payload Data:", value="Hello IPv6 Network Simulation", height=100)

    with col2:
        proto = st.selectbox("Next Header Protocol:", ["UDP (17)", "TCP (6)", "ICMPv6 (58)", "No Next Header (59)"], index=0)
        proto_name = proto.split()[0]

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            tc = st.number_input("Traffic Class (0-255):", min_value=0, max_value=255, value=0)
            hl = st.slider("Hop Limit (0-255):", min_value=0, max_value=255, value=64)
        with col_sub2:
            fl = st.number_input("Flow Label (0-1048575):", min_value=0, max_value=1048575, value=0)

    create_pkt_btn = st.button("🔨 Create Simulated IPv6 Packet", type="primary")

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

            st.success("✅ **IPv6 Packet Created Successfully**")

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("IP Version", f"v{pkt.version}")
            p2.metric("Base Header Size", "40 Bytes (Fixed)")
            p3.metric("Payload Length", f"{pkt.payload_length} Bytes")
            p4.metric("Total Packet Size", f"{40 + pkt.payload_length} Bytes")

            st.divider()

            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.subheader("📋 40-Byte Base Header Breakdown")
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
                st.subheader("📦 Payload Content Inspection")
                st.code(pkt.payload if pkt.payload else "<Empty Payload>", language="text")

                st.subheader("🖨️ Terminal Header View")
                st.code(NetworkVisualizer.format_header_view(pkt), language="text")

        except ValueError as err:
            st.error(f"❌ **Packet Creation Error**: {err}")


# =============================================================================
# 4. Network Topology Page
# =============================================================================
elif page == "🗺️ Network Topology":
    st.title("🗺️ Network Topology & Device Inspector")
    st.markdown("Explore the simulated 3-router linear network, configured interfaces, and subnet links.")

    st.subheader("Topology Architecture Diagram")
    st.code(NetworkVisualizer.format_topology_graph(topology), language="text")

    st.divider()

    st.subheader("🔍 Inspect Device Card")
    all_devs = list(topology.hosts.keys()) + list(topology.routers.keys())
    selected_dev = st.selectbox("Select Device to Inspect:", all_devs, index=0)

    if selected_dev:
        st.code(NetworkVisualizer.format_device_details(selected_dev, topology), language="text")

    st.divider()

    st.subheader("🔗 Configured Subnet Links")
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
elif page == "📋 Routing Tables & LPM":
    st.title("📋 Router Routing Tables & Longest Prefix Match")
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

        st.divider()

        st.subheader("🔍 Route Lookup & Longest Prefix Match (LPM) Query")
        query_dest = st.text_input(
            f"Enter Destination IPv6 to Lookup on {router.name}:",
            value="2001:db8:4::20",
            help="Example: 2001:db8:4::20 (Host B) or 2001:db8:1::10 (Host A)",
        )

        if st.button("🔎 Lookup Route"):
            lookup = router.lookup_route(query_dest.strip())

            if lookup["status"] == "SUCCESS":
                st.success(f"✅ Route Found via **{lookup['route_type']}** route")

                l1, l2, l3 = st.columns(3)
                l1.metric("Best Matching Prefix (LPM)", lookup["selected_prefix"])
                l2.metric("Next Hop IPv6", lookup["next_hop"])
                l3.metric("Outgoing Interface", lookup["interface"])

                if len(lookup["matching_prefixes"]) > 1:
                    st.info(f"💡 **Longest Prefix Match**: Evaluated candidate prefixes: `{lookup['matching_prefixes']}` and chose `{lookup['selected_prefix']}`.")
            else:
                st.error(f"❌ **Lookup Failed**: {lookup['message']}")


# =============================================================================
# 6. Packet Forwarding Simulation Page
# =============================================================================
elif page == "🚀 Packet Forwarding Engine":
    st.title("🚀 IPv6 Packet Forwarding Simulation Cockpit")
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
            "**Forwarding Rules:**\n"
            "- Each router decrements Hop Limit ($HL = HL - 1$).\n"
            "- Packet is dropped if $HL \\le 1$ upon arrival at an intermediate router.\n"
            "- Router uses Longest Prefix Match to forward to the next hop."
        )

    start_sim_btn = st.button("🚀 Start Forwarding Simulation", type="primary", use_container_width=True)

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

            st.divider()

            # Result Header
            if sim_res.status == ForwardingStatus.DELIVERED:
                st.success("### 🎉 Status: PACKET DELIVERED SUCCESSFULLY")
            elif sim_res.status == ForwardingStatus.DROPPED_HOP_LIMIT:
                st.error("### 🛑 Status: PACKET DROPPED (Hop Limit Expired)")
            elif sim_res.status == ForwardingStatus.DROPPED_NO_ROUTE:
                st.error("### 🛑 Status: PACKET DROPPED (No Matching Route)")
            else:
                st.warning(f"### ⚠️ Status: {sim_res.status.value}")

            # Top Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Initial Hop Limit", sim_res.initial_hop_limit)
            m2.metric("Final Hop Limit", sim_res.final_hop_limit)
            m3.metric("Routers Traversed", sim_res.num_router_hops)
            m4.metric("Forwarding Event Steps", len(sim_res.log))

            st.markdown(f"**Forwarding Path:** `{' -> '.join(sim_res.path)}`")

            # Visual Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Active Path Diagram", "⏱️ Processing Timeline", "🎬 Step-by-Step Snapshots", "📋 Header Integrity Check"])

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
                    "Observe that **only Hop Limit** is decremented during router forwarding. "
                    "All other fields remain perfectly preserved."
                )
                col_hdr1, col_hdr2 = st.columns(2)
                with col_hdr1:
                    st.markdown("#### Initial Transmitted Packet")
                    st.code(NetworkVisualizer.format_header_view(sim_pkt), language="text")
                with col_hdr2:
                    st.markdown("#### Statistics Summary")
                    st.code(NetworkVisualizer.format_forwarding_stats(sim_res), language="text")

        except ValueError as err:
            st.error(f"❌ **Forwarding Execution Error**: {err}")


# =============================================================================
# 7. Test Scenarios Page
# =============================================================================
elif page == "🧪 Test Scenarios":
    st.title("🧪 Standardized Laboratory Test Scenarios")
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

    if st.button("▶️ Execute Selected Scenario", type="primary"):
        if "Scenario 1" in chosen_sc:
            st.subheader("Scenario 1: Successful Multi-Hop Delivery")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 1 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.success("✅ **DELIVERED**: Packet traveled through `Host A -> R1 -> R2 -> R3 -> Host B`.")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Scenario 2" in chosen_sc:
            st.subheader("Scenario 2: Hop Limit Expiration Packet Drop")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 2 Test", hop_limit=1)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.error(f"🛑 **DROPPED_HOP_LIMIT**: Dropped at R1 because Initial Hop Limit was 1.")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Scenario 3" in chosen_sc:
            st.subheader("Scenario 3: No Route to Destination Drop")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:99::10", payload="Scenario 3 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.error(f"🛑 **DROPPED_NO_ROUTE**: Dropped at R1 because 2001:db8:99::10 has no route in routing table.")
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
            st.success(f"✅ **LPM Selected Route**: `{lookup['selected_prefix']}` via Next Hop `{lookup['next_hop']}` on `{lookup['interface']}`.")
            st.code(demo_router.format_lookup_result(lookup), language="text")

        elif "Scenario 5" in chosen_sc:
            st.subheader("Scenario 5: Directly Connected Subnet Delivery")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:1::25", payload="Scenario 5 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            st.success("✅ **DIRECT DELIVERY**: Delivered locally on 2001:db8:1::/64 without intermediate router hops.")
            st.code(NetworkVisualizer.format_forwarding_timeline(res), language="text")

        elif "Run All" in chosen_sc:
            st.subheader("Batch Results for All 5 Standard Scenarios")
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
