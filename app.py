"""
IPv6 Packet Processing Simulator - CLI Application (Phase 1)

This application demonstrates IPv6 address parsing, validation, representation,
type classification, and subnet analysis from the command line.
"""

import sys
from src.ipv6_address import IPv6AddressAnalyzer, analyze_ipv6


def display_banner():
    """Print project header banner."""
    print("=" * 60)
    print("      IPv6 PACKET PROCESSING SIMULATOR - PHASE 1")
    print("             IPv6 Addressing & Subnet Analyzer")
    print("=" * 60)


def process_and_display(address_input: str):
    """Analyze the given input and print the formatted report."""
    result = analyze_ipv6(address_input)
    report = IPv6AddressAnalyzer.format_report(result)
    print()
    print(report)
    print()


def run_sample_demonstration():
    """Run a pre-configured showcase of various IPv6 address types."""
    samples = [
        ("Global / Documentation Address", "2001:db8:1::10"),
        ("Subnet & Prefix Analysis (/64)", "2001:db8:1::10/64"),
        ("Loopback Address", "::1"),
        ("Unspecified Address", "::"),
        ("Link-Local Unicast Address", "fe80::1"),
        ("Multicast Address", "ff02::1"),
        ("Unique-Local (Private) Address", "fd12:3456:789a:1::1/64"),
        ("Global Unicast Address", "2607:f8b0:4005:805::200e"),
        ("Invalid IPv6 Address (Demonstration)", "2001:xyz::1"),
    ]

    print("\n--- Running Built-in IPv6 Showcase Demonstration ---\n")
    for label, sample in samples:
        print(f"[{label}]")
        process_and_display(sample)
        print("-" * 60)


def interactive_mode():
    """Run the interactive command-line loop."""
    display_banner()

    while True:
        print("Menu Options:")
        print("  1. Analyze an IPv6 Address or Subnet (CIDR)")
        print("  2. Run Built-in Showcase Demonstration")
        print("  3. Exit")
        print()

        try:
            choice = input("Select an option (1-3): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if choice == "1":
            try:
                user_input = input("\nEnter IPv6 address or network (e.g., 2001:db8:1::10 or 2001:db8:1::10/64): ").strip()
                if user_input:
                    process_and_display(user_input)
                else:
                    print("Error: Input cannot be empty.\n")
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
        elif choice == "2":
            run_sample_demonstration()
        elif choice == "3" or choice.lower() in ("q", "quit", "exit"):
            print("\nExiting IPv6 Packet Processing Simulator. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1, 2, or 3.\n")


def main():
    """Entry point for CLI execution."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ("--demo", "-d", "demo"):
            display_banner()
            run_sample_demonstration()
        elif arg in ("--help", "-h", "help"):
            print("Usage:")
            print("  python app.py                      # Interactive menu mode")
            print("  python app.py <ipv6_address>       # Direct analysis (e.g. 2001:db8:1::10)")
            print("  python app.py <ipv6_prefix>        # Subnet analysis (e.g. 2001:db8:1::10/64)")
            print("  python app.py --demo               # Run showcase demo")
        else:
            process_and_display(arg)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
