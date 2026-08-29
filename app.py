"""
IPv6 Packet Processing Simulator - CLI Application (Phase 1, Phase 2, & Phase 3)

This application provides:
1. Phase 1: IPv6 address parsing, validation, classification, and subnet analysis.
2. Phase 2: IPv6 packet creation, base header simulation, and payload inspection.
3. Phase 3: Simulated routers, IPv6 interfaces, routing tables, and Longest Prefix Match (LPM).
"""

import sys
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6
from src.ipv6_packet import IPv6Packet, create_ipv6_packet
from src.router import Router
from src.network import NetworkTopology, build_sample_topology


def display_banner():
    """Print project header banner."""
    print("=" * 65)
    print("      IPv6 PACKET PROCESSING SIMULATOR (PHASE 1, 2, & 3)")
    print(" Addressing Engine | Packet Simulation | Routers & Routing Tables")
    print("=" * 65)


def process_and_display_address(address_input: str):
    """Analyze the given IPv6 address input and print the formatted report."""
    result = analyze_ipv6(address_input)
    report = IPv6AddressAnalyzer.format_report(result)
    print()
    print(report)
    print()


def interactive_packet_creation():
    """Prompt user for packet fields, create and display the simulated IPv6 packet."""
    print("\n--- Create & Simulate an IPv6 Packet ---")
    try:
        src = input("Source IPv6 Address      : ").strip()
        if not src:
            print("Error: Source address cannot be empty.\n")
            return

        dst = input("Destination IPv6 Address : ").strip()
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

        print("\nCreating IPv6 Packet...")
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
        print(packet.display_header())
        print()

        # Display forwarding summary
        summary = packet.get_summary()
        print("Packet Forwarding Summary:")
        print(f"  Source      : {summary['source']}")
        print(f"  Destination : {summary['destination']}")
        print(f"  Protocol    : {summary['next_header']}")
        print(f"  Payload Size: {summary['payload_length']} bytes")
        print(f"  Hop Limit   : {summary['hop_limit']}")
        print()

    except ValueError as err:
        print(f"\n[Packet Creation Error]: {err}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nPacket creation cancelled.\n")


def interactive_router_menu(topology: NetworkTopology):
    """Submenu for Router and Routing Table operations."""
    while True:
        print("\n--- Router & Routing Table Submenu ---")
        print("  1. Display Network Topology Diagram")
        print("  2. Inspect Router (Interfaces & Routing Table)")
        print("  3. Perform Route Lookup (Longest Prefix Match)")
        print("  4. Demonstrate LPM with Overlapping Prefixes")
        print("  5. Return to Main Menu")
        print()

        try:
            choice = input("Select an option (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            print()
            print(topology.display_topology())
            print()
        elif choice == "2":
            print(f"\nAvailable Routers: {', '.join(topology.routers.keys())}")
            r_name = input("Enter router name (e.g. R1, R2, R3): ").strip()
            router = topology.get_router(r_name)
            if router:
                print()
                print(router.display_router_info())
                print()
            else:
                print(f"Error: Router '{r_name}' not found in topology.\n")
        elif choice == "3":
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
        elif choice == "4":
            demonstrate_lpm()
        elif choice == "5" or choice.lower() in ("b", "back"):
            break
        else:
            print("\nInvalid choice. Please select 1-5.\n")


def demonstrate_lpm():
    """Demonstrate Longest Prefix Match resolution using overlapping routes."""
    print("\n" + "=" * 65)
    print("      LONGEST PREFIX MATCH (LPM) DEMONSTRATION")
    print("=" * 65)
    demo_router = Router("DemoRouter")
    demo_router.add_interface("eth0", "2001:db8:0::1/32")
    demo_router.add_interface("eth1", "2001:db8:4::1/48")
    demo_router.add_interface("eth2", "2001:db8:4:10::1/64")

    # Add overlapping static routes
    demo_router.add_static_route("2001:db8::/32", next_hop="2001:db8:0::10", interface="eth0")
    demo_router.add_static_route("2001:db8:4::/48", next_hop="2001:db8:4::10", interface="eth1")
    demo_router.add_static_route("2001:db8:4:10::/64", next_hop="2001:db8:4:10::10", interface="eth2")

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
        print("-" * 65)


def run_sample_demonstration():
    """Run a complete showcase of Phase 1, Phase 2, and Phase 3 features."""
    topo = build_sample_topology()

    print("\n" + "=" * 65)
    print("             PHASE 1: IPv6 ADDRESSING SHOWCASE")
    print("=" * 65)

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
        print("-" * 65)

    print("\n" + "=" * 65)
    print("          PHASE 2: IPv6 PACKET SIMULATION SHOWCASE")
    print("=" * 65)

    packet_samples = [
        (
            "Sample 1: UDP Data Packet (Default Flow)",
            "2001:db8:1::10",
            "2001:db8:4::20",
            "Hello IPv6",
            0,
            0,
            "UDP",
            64,
        ),
        (
            "Sample 2: TCP SYN Packet (QoS Traffic Class)",
            "2001:db8:1::100",
            "2001:db8:2::200",
            "SYN_REQ",
            64,
            12345,
            "TCP",
            128,
        ),
        (
            "Sample 3: ICMPv6 Ping Request",
            "fe80::1",
            "ff02::1",
            "EchoRequest",
            0,
            0,
            "ICMPv6",
            255,
        ),
        (
            "Sample 4: No Next Header Packet",
            "2001:db8::1",
            "2001:db8::2",
            "",
            0,
            0,
            59,
            64,
        ),
    ]

    for label, src, dst, payload, tc, fl, proto, hl in packet_samples:
        print(f"\n[{label}]")
        pkt = create_ipv6_packet(
            source_address=src,
            destination_address=dst,
            payload=payload,
            traffic_class=tc,
            flow_label=fl,
            next_header=proto,
            hop_limit=hl,
        )
        print(pkt.display_header())
        print("-" * 65)

    print("\n" + "=" * 65)
    print("       PHASE 3: ROUTERS, ROUTING TABLES & LPM SHOWCASE")
    print("=" * 65)

    # 1. Topology display
    print(topo.display_topology())
    print()

    # 2. Display R1 routing table
    r1 = topo.get_router("R1")
    if r1:
        print(r1.display_router_info())
        print()

        # 3. Route lookup on R1 for Host B
        print("[Route Lookup: R1 -> Host B (2001:db8:4::20)]")
        res = r1.lookup_route("2001:db8:4::20")
        print(r1.format_lookup_result(res))
        print("-" * 65)

    # 4. Longest Prefix Match Showcase
    demonstrate_lpm()


def interactive_mode():
    """Run the interactive command-line loop."""
    topology = build_sample_topology()
    display_banner()

    while True:
        print("Main Menu:")
        print("  1. Analyze an IPv6 Address or Subnet (Phase 1)")
        print("  2. Create & Simulate an IPv6 Packet (Phase 2)")
        print("  3. Simulated Routers & IPv6 Routing Tables (Phase 3)")
        print("  4. Run Built-in Showcase Demonstrations (Phase 1, 2, & 3)")
        print("  5. Exit")
        print()

        try:
            choice = input("Select an option (1-5): ").strip()
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
            interactive_router_menu(topology)
        elif choice == "4":
            run_sample_demonstration()
        elif choice == "5" or choice.lower() in ("q", "quit", "exit"):
            print("\nExiting IPv6 Packet Processing Simulator. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1, 2, 3, 4, or 5.\n")


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
            print("  python app.py                                   # Interactive menu mode")
            print("  python app.py <ipv6_address>                    # Analyze address (Phase 1)")
            print("  python app.py <ipv6_cidr>                       # Analyze subnet (Phase 1)")
            print("  python app.py packet <src> <dst> [payload] [proto] [hop]")
            print("  python app.py topology                          # Display network topology")
            print("  python app.py route <router_name> <dest_ip>     # Perform route lookup on router")
            print("  python app.py --demo                            # Run full showcase demo")
        elif first_arg == "topology":
            print(topology.display_topology())
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
        elif first_arg == "packet":
            # Direct packet creation mode via CLI
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
                print(pkt.display_header())
            except ValueError as err:
                print(f"Error creating packet: {err}")
        else:
            # Address analysis
            process_and_display_address(first_arg)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
