"""
IPv6 Packet Processing Simulator - Standalone Laboratory Demonstration Script (Phase 6)

This script executes a complete, zero-input, automated demonstration of:
1. Simulated Network Topology Creation
2. IPv6 Packet Modeling and Header Construction
3. Hop-by-Hop Packet Forwarding across R1 -> R2 -> R3
4. Longest Prefix Match (LPM) and Route Decision Tracking
5. Hop Limit Decrementing (64 -> 61)
6. Step-by-Step Movement Snapshots and Event Timeline
"""

from src.ipv6_packet import create_ipv6_packet
from src.network import build_sample_topology
from src.forwarding import forward_packet
from src.visualization import NetworkVisualizer


def run_laboratory_demo():
    """Run the complete end-to-end laboratory demonstration."""
    print("=" * 70)
    print("      IPv6 PACKET PROCESSING SIMULATOR - LABORATORY DEMO")
    print("=" * 70)
    print()

    # Step 1: Initialize Network Topology
    print("[STEP 1: Initializing 3-Router Linear Network Topology]")
    topology = build_sample_topology()
    print(NetworkVisualizer.format_topology_graph(topology))
    print()

    # Step 2: Create Simulated IPv6 Packet
    print("[STEP 2: Constructing Simulated IPv6 Packet]")
    src_ip = "2001:db8:1::10"
    dst_ip = "2001:db8:4::20"
    payload = "Hello IPv6"
    initial_hl = 64

    packet = create_ipv6_packet(
        source_address=src_ip,
        destination_address=dst_ip,
        payload=payload,
        next_header="UDP",
        hop_limit=initial_hl,
    )
    print(NetworkVisualizer.format_header_view(packet))
    print()

    # Step 3: Execute Forwarding Engine
    print("[STEP 3: Executing Hop-by-Hop Packet Forwarding Engine]")
    result = forward_packet(
        packet=packet,
        topology=topology,
        source_host_name="Host A",
    )

    # Step 4: Step-by-Step Movement Snapshots
    print("[STEP 4: Step-by-Step Packet Movement Snapshots]")
    print("-" * 70)
    snapshots = NetworkVisualizer.format_packet_movement_steps(result)
    for s in snapshots:
        print(s)
        print()

    # Step 5: Forwarding Timeline
    print("[STEP 5: Packet Processing Event Timeline]")
    print(NetworkVisualizer.format_forwarding_timeline(result))
    print()

    # Step 6: Forwarding Statistics & Final Result
    print("[STEP 6: Final Forwarding Statistics & Summary]")
    print(NetworkVisualizer.format_forwarding_stats(result))
    print()
    print("=" * 70)
    print("        LABORATORY DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_laboratory_demo()
