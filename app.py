"""
IPv6 Packet Processing Simulator - Interactive Dashboard & CLI Application (Phases 1 - 6)

Educational Computer Networks Laboratory Simulator providing:
1. IPv6 address validation, RFC 5952 formatting, classification, and subnet analysis.
2. Fixed 40-byte IPv6 base header creation and field inspection.
3. Multi-interface router simulation, routing tables, and Longest Prefix Match (LPM).
4. Hop-by-hop packet forwarding across multi-router network topologies.
5. Interactive visual diagrams, device cards, packet movement snapshots, and timelines.
6. Predefined educational test scenario runners.
"""

from __future__ import annotations

import sys
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6
from src.ipv6_packet import IPv6Packet, create_ipv6_packet
from src.router import Router
from src.host import Host, Link
from src.network import NetworkTopology, build_sample_topology
from src.forwarding import ForwardingResult, ForwardingStatus, PacketForwarder, forward_packet
from src.visualization import NetworkVisualizer


def display_banner():
    """Print project header banner."""
    print("=" * 70)
    print("             IPv6 PACKET PROCESSING SIMULATOR")
    print(" Educational Computer Networks Laboratory Simulation Dashboard")
    print("=" * 70)


def process_and_display_address(address_input: str):
    """Analyze the given IPv6 address input and print formatted report."""
    result = analyze_ipv6(address_input)
    report = IPv6AddressAnalyzer.format_report(result)
    print()
    print(report)
    print()


def interactive_packet_creation():
    """Prompt user for packet fields, create and display the simulated IPv6 packet."""
    print("\n" + "=" * 70)
    print("             [2] IPv6 PACKET & HEADER SIMULATOR")
    print("=" * 70)
    try:
        src = input("Source IPv6 Address      (e.g. 2001:db8:1::10) : ").strip()
        if not src:
            print("Error: Source address cannot be empty.\n")
            return

        dst = input("Destination IPv6 Address (e.g. 2001:db8:4::20) : ").strip()
        if not dst:
            print("Error: Destination address cannot be empty.\n")
            return

        payload = input("Payload (default 'Hello IPv6'): ").strip()
        if not payload:
            payload = "Hello IPv6"

        tc_input = input("Traffic Class [0-255] (default 0): ").strip()
        tc = int(tc_input) if tc_input else 0

        fl_input = input("Flow Label [0-1048575] (default 0): ").strip()
        fl = int(fl_input) if fl_input else 0

        proto_input = input("Next Header [UDP/TCP/ICMPv6/59] (default UDP): ").strip()
        proto = proto_input if proto_input else "UDP"

        hl_input = input("Hop Limit [0-255] (default 64): ").strip()
        hl = int(hl_input) if hl_input else 64

        print("\nConstructing IPv6 Packet...")
        packet = create_ipv6_packet(
            source_address=src,
            destination_address=dst,
            payload=payload,
            traffic_class=tc,
            flow_label=fl,
            next_header=proto,
            hop_limit=hl,
        )

        print()
        print(NetworkVisualizer.format_header_view(packet))
        print()

    except ValueError as err:
        print(f"\n[Packet Creation Error]: {err}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nPacket creation cancelled.\n")


def interactive_device_inspector(topology: NetworkTopology):
    """Submenu for inspecting network topology and devices."""
    while True:
        print("\n" + "=" * 70)
        print("          [3] NETWORK TOPOLOGY & DEVICE INSPECTOR")
        print("=" * 70)
        print("  1. View Network Architecture Diagram")
        print("  2. Inspect Device Card (Host A, Host B, R1, R2, R3)")
        print("  3. List All Configured Links & Subnets")
        print("  4. Return to Main Menu")
        print()

        try:
            choice = input("Select an option (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            print()
            print(NetworkVisualizer.format_topology_graph(topology))
            print()
        elif choice == "2":
            all_devices = list(topology.hosts.keys()) + list(topology.routers.keys())
            print(f"\nAvailable Devices: {', '.join(all_devices)}")
            dev_name = input("Enter device name (e.g. Host A, R1): ").strip()
            if dev_name:
                print()
                print(NetworkVisualizer.format_device_details(dev_name, topology))
                print()
            else:
                print("Error: Device name cannot be empty.\n")
        elif choice == "3":
            print("\nConfigured Subnet Links:")
            print("-" * 65)
            for link in topology.links:
                print(f"  {link.node_a} ({link.interface_a}) <---> {link.node_b} ({link.interface_b}) on Subnet: {link.network}")
            print("-" * 65 + "\n")
        elif choice == "4" or choice.lower() in ("b", "back"):
            break
        else:
            print("\nInvalid choice. Please select 1-4.\n")


def interactive_routing_menu(topology: NetworkTopology):
    """Submenu for Router and Routing Table operations."""
    while True:
        print("\n" + "=" * 70)
        print("          [4] ROUTING TABLES & LPM INSPECTOR")
        print("=" * 70)
        print("  1. Display Router Routing Table (R1, R2, R3)")
        print("  2. Perform Route Lookup on Router")
        print("  3. Demonstrate Longest Prefix Match (LPM) Showcase")
        print("  4. Return to Main Menu")
        print()

        try:
            choice = input("Select an option (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            print(f"\nAvailable Routers: {', '.join(topology.routers.keys())}")
            r_name = input("Enter router name (e.g. R1, R2, R3): ").strip()
            router = topology.get_router(r_name)
            if router:
                print()
                print(router.display_router_info())
                print()
            else:
                print(f"Error: Router '{r_name}' not found in topology.\n")
        elif choice == "2":
            print(f"\nAvailable Routers: {', '.join(topology.routers.keys())}")
            r_name = input("Select Router (e.g. R1): ").strip()
            router = topology.get_router(r_name)
            if not router:
                print(f"Error: Router '{r_name}' not found.\n")
                continue

            dest_ip = input("Enter Destination IPv6 Address (e.g. 2001:db8:4::20): ").strip()
            if not dest_ip:
                print("Error: Destination address cannot be empty.\n")
                continue

            result = router.lookup_route(dest_ip)
            print()
            print(router.format_lookup_result(result))
            print()
        elif choice == "3":
            demonstrate_lpm()
        elif choice == "4" or choice.lower() in ("b", "back"):
            break
        else:
            print("\nInvalid choice. Please select 1-4.\n")


def interactive_forwarding_dashboard(topology: NetworkTopology):
    """Interactive forwarding simulation visual dashboard."""
    print("\n" + "=" * 70)
    print("             [5] IPv6 PACKET FORWARDING SIMULATION")
    print("=" * 70)
    print("Configured Network Hosts:")
    for h in topology.hosts.values():
        print(f"  - {h.name}: {h.ipv6_address} (Subnet: {h.network}, Gateway: {h.default_gateway})")
    print()

    try:
        # 1. Source Selection
        src_choice = input("Enter Source Host name or IPv6 address (default 'Host A'): ").strip()
        if not src_choice:
            src_choice = "Host A"

        src_ip = src_choice
        src_host_obj = topology.get_host(src_choice)
        if src_host_obj:
            src_ip = src_host_obj.ipv6_address

        # 2. Destination Selection
        dst_choice = input("Enter Destination Host name or IPv6 address (default 'Host B'): ").strip()
        if not dst_choice:
            dst_choice = "Host B"

        dst_ip = dst_choice
        dst_host_obj = topology.get_host(dst_choice)
        if dst_host_obj:
            dst_ip = dst_host_obj.ipv6_address

        payload = input("Enter Payload data (default 'Hello IPv6'): ").strip()
        if not payload:
            payload = "Hello IPv6"

        proto = input("Enter Next Header Protocol [UDP/TCP/ICMPv6] (default UDP): ").strip()
        if not proto:
            proto = "UDP"

        hl_input = input("Enter Initial Hop Limit (default 64, or 1 to test drop): ").strip()
        hl = int(hl_input) if hl_input else 64

        # Create Packet
        packet = create_ipv6_packet(
            source_address=src_ip,
            destination_address=dst_ip,
            payload=payload,
            next_header=proto,
            hop_limit=hl,
        )

        print("\nExecuting Hop-by-Hop Forwarding Engine...\n")
        result = forward_packet(
            packet=packet,
            topology=topology,
            source_host_name=src_host_obj.name if src_host_obj else None,
        )

        # 1. Packet Header View
        print(NetworkVisualizer.format_header_view(packet))
        print()

        # 2. Topology Diagram with Highlighted Path
        print(NetworkVisualizer.format_topology_graph(topology, active_path=result.path))
        print()

        # 3. Movement Snapshots
        print("=" * 70)
        print("          STEP-BY-STEP PACKET MOVEMENT SNAPSHOTS")
        print("=" * 70)
        snapshots = NetworkVisualizer.format_packet_movement_steps(result)
        for s in snapshots:
            print(s)
            print()

        # 4. Processing Timeline
        print(NetworkVisualizer.format_forwarding_timeline(result))
        print()

        # 5. Statistics
        print(NetworkVisualizer.format_forwarding_stats(result))
        print()

    except ValueError as err:
        print(f"\n[Forwarding Error]: {err}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nForwarding simulation cancelled.\n")


def interactive_scenario_runner(topology: NetworkTopology):
    """Submenu to execute predefined educational test scenarios."""
    while True:
        print("\n" + "=" * 70)
        print("           [6] PREDEFINED TEST SCENARIOS RUNNER")
        print("=" * 70)
        print("  1. Scenario 1: Successful Multi-Hop Delivery (Host A -> Host B)")
        print("  2. Scenario 2: Hop Limit Expiration Packet Drop (Hop Limit = 1)")
        print("  3. Scenario 3: No Route to Destination Drop (2001:db8:99::10)")
        print("  4. Scenario 4: Longest Prefix Match (LPM) Selection")
        print("  5. Scenario 5: Directly Connected Subnet Delivery")
        print("  6. Run All 5 Standard Scenarios Sequentially")
        print("  7. Return to Main Menu")
        print()

        try:
            choice = input("Select an option (1-7): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            print("\n[Executing Scenario 1: Successful Multi-Hop Delivery]")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 1 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            print(NetworkVisualizer.format_forwarding_timeline(res))
            print(NetworkVisualizer.format_forwarding_stats(res))
        elif choice == "2":
            print("\n[Executing Scenario 2: Hop Limit Expiration Drop]")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Scenario 2 Test", hop_limit=1)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            print(NetworkVisualizer.format_forwarding_timeline(res))
            print(NetworkVisualizer.format_forwarding_stats(res))
        elif choice == "3":
            print("\n[Executing Scenario 3: No Matching Route Drop]")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:99::10", payload="Scenario 3 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            print(NetworkVisualizer.format_forwarding_timeline(res))
            print(NetworkVisualizer.format_forwarding_stats(res))
        elif choice == "4":
            demonstrate_lpm()
        elif choice == "5":
            print("\n[Executing Scenario 5: Directly Connected Subnet Delivery]")
            pkt = create_ipv6_packet("2001:db8:1::10", "2001:db8:1::25", payload="Scenario 5 Test", hop_limit=64)
            res = forward_packet(pkt, topology, source_host_name="Host A")
            print(NetworkVisualizer.format_forwarding_timeline(res))
            print(NetworkVisualizer.format_forwarding_stats(res))
        elif choice == "6":
            print("\nRunning all 5 scenarios sequentially...\n")
            for sc_idx, (src, dst, hl, label) in enumerate([
                ("2001:db8:1::10", "2001:db8:4::20", 64, "Scenario 1: Successful Delivery"),
                ("2001:db8:1::10", "2001:db8:4::20", 1, "Scenario 2: Hop Limit Expiration Drop"),
                ("2001:db8:1::10", "2001:db8:99::10", 64, "Scenario 3: No Route Drop"),
                ("2001:db8:1::10", "2001:db8:1::25", 64, "Scenario 5: Directly Connected Subnet Delivery"),
            ], start=1):
                print(f"--- [{label}] ---")
                pkt = create_ipv6_packet(src, dst, payload=f"Batch {sc_idx}", hop_limit=hl)
                res = forward_packet(pkt, topology, source_host_name="Host A")
                print(f"Outcome : {res.status.value} | Path: {' -> '.join(res.path)} | HL: {res.initial_hop_limit} -> {res.final_hop_limit}")
                print()
            print("--- [Scenario 4: Longest Prefix Match Demo] ---")
            demonstrate_lpm()
        elif choice == "7" or choice.lower() in ("b", "back"):
            break
        else:
            print("\nInvalid choice. Please select 1-7.\n")


def demonstrate_lpm():
    """Demonstrate Longest Prefix Match resolution using overlapping routes."""
    print("\n" + "=" * 70)
    print("      LONGEST PREFIX MATCH (LPM) DEMONSTRATION")
    print("=" * 70)
    demo_router = Router("DemoRouter")
    demo_router.add_interface("eth0", "2001:db8:0::1/32")
    demo_router.add_interface("eth1", "2001:db8:4::1/48")
    demo_router.add_interface("eth2", "2001:db8:4:10::1/64")

    # Add overlapping static routes
    demo_router.add_static_route("2001:db8::/32", next_hop="2001:db8:10::1", interface="eth0")
    demo_router.add_static_route("2001:db8:4::/48", next_hop="2001:db8:10::2", interface="eth1")
    demo_router.add_static_route("2001:db8:4:10::/64", next_hop="2001:db8:10::3", interface="eth2")

    print("\nConfigured Routing Table on DemoRouter:")
    print(demo_router.routing_table.display_table())

    test_destinations = [
        ("2001:db8:4:10::20", "Matches /32, /48, and /64 -> Selects /64 (Longest Prefix)"),
        ("2001:db8:4:99::5", "Matches /32 and /48 -> Selects /48 (Fallback)"),
        ("2001:db8:8888::1", "Matches /32 only -> Selects /32"),
        ("2001:cafe::1", "No matching route -> Returns No Route"),
    ]

    for dest, desc in test_destinations:
        print(f"\n[Test Destination: {dest}] ({desc})")
        res = demo_router.lookup_route(dest)
        print(demo_router.format_lookup_result(res))
        print("-" * 70)


def run_sample_demonstration():
    """Run a complete showcase across all Phases (1 - 6)."""
    topo = build_sample_topology()

    print("\n" + "=" * 70)
    print("             PHASE 1: IPv6 ADDRESSING SHOWCASE")
    print("=" * 70)

    address_samples = [
        ("Global / Documentation Address", "2001:db8:1::10"),
        ("Subnet & Prefix Analysis (/64)", "2001:db8:1::10/64"),
        ("Loopback Address", "::1"),
        ("Link-Local Unicast Address", "fe80::1"),
        ("Multicast Address", "ff02::1"),
        ("Unique-Local Address", "fd12:3456:789a:1::1/64"),
        ("Invalid Address Demonstration", "2001:xyz::1"),
    ]

    for label, sample in address_samples:
        print(f"[{label}]")
        process_and_display_address(sample)
        print("-" * 70)

    print("\n" + "=" * 70)
    print("          PHASE 2: IPv6 PACKET SIMULATION SHOWCASE")
    print("=" * 70)

    pkt_demo = create_ipv6_packet(
        source_address="2001:db8:1::10",
        destination_address="2001:db8:4::20",
        payload="Hello IPv6",
        next_header="UDP",
        hop_limit=64,
    )
    print(NetworkVisualizer.format_header_view(pkt_demo))
    print("-" * 70)

    print("\n" + "=" * 70)
    print("       PHASE 3: ROUTERS, ROUTING TABLES & LPM SHOWCASE")
    print("=" * 70)

    # Topology display
    print(NetworkVisualizer.format_topology_graph(topo))
    print()

    # Route lookup on R1 for Host B
    r1 = topo.get_router("R1")
    if r1:
        print(r1.display_router_info())
        print()
        print("[Route Lookup: R1 -> Host B (2001:db8:4::20)]")
        res = r1.lookup_route("2001:db8:4::20")
        print(r1.format_lookup_result(res))
        print("-" * 70)

    # Longest Prefix Match Showcase
    demonstrate_lpm()

    print("\n" + "=" * 70)
    print("   PHASE 4, 5 & 6: PACKET FORWARDING & VISUAL DASHBOARD")
    print("=" * 70)

    # 1. Successful Multi-Hop Delivery Dashboard
    print("\n[Scenario 1: Successful Multi-Hop Forwarding (Host A -> Host B)]")
    pkt1 = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Hello from Host A", hop_limit=64)
    res1 = forward_packet(pkt1, topo, source_host_name="Host A")
    print(NetworkVisualizer.format_topology_graph(topo, active_path=res1.path))
    print()
    print(NetworkVisualizer.format_forwarding_timeline(res1))
    print()
    print(NetworkVisualizer.format_forwarding_stats(res1))
    print("-" * 70)

    # 2. Hop Limit Expiration Drop
    print("\n[Scenario 2: Hop Limit Expiration Drop (Initial Hop Limit = 1)]")
    pkt2 = create_ipv6_packet("2001:db8:1::10", "2001:db8:4::20", payload="Expiring Packet", hop_limit=1)
    res2 = forward_packet(pkt2, topo, source_host_name="Host A")
    print(NetworkVisualizer.format_forwarding_timeline(res2))
    print()
    print(NetworkVisualizer.format_forwarding_stats(res2))
    print("-" * 70)

    # 3. No Route Drop
    print("\n[Scenario 3: No Matching Route Drop (Destination: 2001:db8:99::10)]")
    pkt3 = create_ipv6_packet("2001:db8:1::10", "2001:db8:99::10", payload="Unroutable Packet", hop_limit=64)
    res3 = forward_packet(pkt3, topo, source_host_name="Host A")
    print(NetworkVisualizer.format_forwarding_timeline(res3))
    print()
    print(NetworkVisualizer.format_forwarding_stats(res3))
    print("-" * 70)


def interactive_mode():
    """Run the interactive command-line loop."""
    topology = build_sample_topology()
    display_banner()

    while True:
        print("Main Menu:")
        print("  [1] IPv6 Address Analyzer (Phase 1)")
        print("  [2] IPv6 Packet Simulator (Phase 2)")
        print("  [3] Network Topology & Device Inspector (Phase 3 & 5)")
        print("  [4] Routing Tables & LPM Inspector (Phase 3 & 5)")
        print("  [5] Packet Forwarding Simulation (Phase 4 & 5)")
        print("  [6] Predefined Test Scenarios Runner (Phase 6)")
        print("  [7] Complete Showcase Demonstration (Phases 1 - 6)")
        print("  [8] Exit")
        print()

        try:
            choice = input("Select an option (1-8): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if choice == "1":
            try:
                user_input = input("\nEnter IPv6 address or CIDR network (e.g. 2001:db8:1::10 or 2001:db8:1::10/64): ").strip()
                if user_input:
                    process_and_display_address(user_input)
                else:
                    print("Error: Address input cannot be empty.\n")
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.\n")
        elif choice == "2":
            interactive_packet_creation()
        elif choice == "3":
            interactive_device_inspector(topology)
        elif choice == "4":
            interactive_routing_menu(topology)
        elif choice == "5":
            interactive_forwarding_dashboard(topology)
        elif choice == "6":
            interactive_scenario_runner(topology)
        elif choice == "7":
            run_sample_demonstration()
        elif choice == "8" or choice.lower() in ("q", "quit", "exit"):
            print("\nExiting IPv6 Packet Processing Simulator. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1, 2, 3, 4, 5, 6, 7, or 8.\n")


def main():
    """Entry point for CLI execution."""
    topology = build_sample_topology()

    if len(sys.argv) > 1:
        first_arg = sys.argv[1].strip()

        if first_arg in ("--demo", "-d", "demo"):
            display_banner()
            run_sample_demonstration()
        elif first_arg in ("--help", "-h", "help"):
            print("Usage:")
            print("  python app.py                                              # Interactive dashboard mode")
            print("  python demo.py                                             # Standalone laboratory demo")
            print("  python app.py <ipv6_address>                               # Analyze address (Phase 1)")
            print("  python app.py <ipv6_cidr>                                  # Analyze subnet (Phase 1)")
            print("  python app.py packet <src> <dst> [payload] [proto] [hop]   # Simulate packet (Phase 2)")
            print("  python app.py topology                                     # Display network topology (Phase 3 & 5)")
            print("  python app.py device <device_name>                         # Inspect device card (Phase 5)")
            print("  python app.py route <router_name> <dest_ip>                # Route lookup (Phase 3)")
            print("  python app.py forward <src_host_or_ip> <dst_host_or_ip> [payload] [hop_limit]")
            print("  python app.py --demo                                       # Run full showcase demo")
        elif first_arg == "topology":
            print(NetworkVisualizer.format_topology_graph(topology))
        elif first_arg == "device":
            if len(sys.argv) < 3:
                print("Usage: python app.py device <device_name>")
                return
            dev_name = sys.argv[2]
            print(NetworkVisualizer.format_device_details(dev_name, topology))
        elif first_arg == "route":
            if len(sys.argv) < 4:
                print("Usage: python app.py route <router_name> <destination_ip>")
                return
            r_name = sys.argv[2]
            dest_ip = sys.argv[3]
            router = topology.get_router(r_name)
            if not router:
                print(f"Error: Router '{r_name}' not found. Available: {', '.join(topology.routers.keys())}")
                return
            result = router.lookup_route(dest_ip)
            print(router.format_lookup_result(result))
        elif first_arg == "forward":
            if len(sys.argv) < 4:
                print("Usage: python app.py forward <src_host_or_ip> <dst_host_or_ip> [payload] [hop_limit]")
                return
            src_arg = sys.argv[2]
            dst_arg = sys.argv[3]
            payload = sys.argv[4] if len(sys.argv) > 4 else "Hello IPv6"
            hl = int(sys.argv[5]) if len(sys.argv) > 5 else 64

            # Resolve host names or direct IPs
            src_host = topology.get_host(src_arg)
            src_ip = src_host.ipv6_address if src_host else src_arg

            dst_host = topology.get_host(dst_arg)
            dst_ip = dst_host.ipv6_address if dst_host else dst_arg

            try:
                pkt = create_ipv6_packet(
                    source_address=src_ip,
                    destination_address=dst_ip,
                    payload=payload,
                    hop_limit=hl,
                )
                res = forward_packet(
                    packet=pkt,
                    topology=topology,
                    source_host_name=src_host.name if src_host else None,
                )
                print(NetworkVisualizer.format_header_view(pkt))
                print()
                print(NetworkVisualizer.format_topology_graph(topology, active_path=res.path))
                print()
                print(NetworkVisualizer.format_forwarding_timeline(res))
                print()
                print(NetworkVisualizer.format_forwarding_stats(res))
            except ValueError as err:
                print(f"Forwarding execution error: {err}")
        elif first_arg == "packet":
            if len(sys.argv) < 4:
                print("Usage: python app.py packet <src_addr> <dst_addr> [payload] [next_header] [hop_limit]")
                return
            src = sys.argv[2]
            dst = sys.argv[3]
            payload = sys.argv[4] if len(sys.argv) > 4 else "Hello IPv6"
            proto = sys.argv[5] if len(sys.argv) > 5 else "UDP"
            hl = int(sys.argv[6]) if len(sys.argv) > 6 else 64
            try:
                pkt = create_ipv6_packet(src, dst, payload=payload, next_header=proto, hop_limit=hl)
                print(NetworkVisualizer.format_header_view(pkt))
            except ValueError as err:
                print(f"Error creating packet: {err}")
        else:
            # Address analysis
            process_and_display_address(first_arg)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
