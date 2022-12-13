#!/usr/bin/env python
""" Compute emissions for a networking emissions """
import argparse
import logging

from scope3_methodology.api.input_models import NetworkingConnectionType
from scope3_methodology.networking.model import NetworkingConnection
from scope3_methodology.networking.transmission_rate_model import TransmissionRate
from scope3_methodology.utils.yaml_helpers import yaml_dump


def parse_args():
    """Parse the command line arguments"""
    # arse command line to get company file
    parser = argparse.ArgumentParser(description="Compute emissions for an publisher")
    parser.add_argument(
        "-f",
        "--defaultsFile",
        default="defaults/networking-defaults.yaml",
        help="Set the defaults file to use (overrides networking-defaults.yaml)",
    )
    parser.add_argument(
        "-t",
        "--transmissionRatesdefaultsFile",
        default="defaults/transmission_rate-defaults.yaml",
        help="Set the defaults file to use (overrides transmission_rate-defaults.yaml)",
    )
    parser.add_argument(
        "-c",
        "--connection",
        const=1,
        default=NetworkingConnectionType.UNKNOWN.value,
        type=str,
        nargs="?",
        help="Networking connection type: unknown, fixed, mobile",
    )
    parser.add_argument(
        "-d",
        "--device",
        const=1,
        default="personal_computer",
        type=str,
        nargs="?",
        help="Environment to model: personal_computer, smartphone, tablet, tv_system",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")

    return parser.parse_args()


def main():
    """Model the emisisons for networking emissions"""
    # Process Command Line Arguments
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    device = str(args.device)
    connection = str(args.connection)
    connection_networking = NetworkingConnection.load_default_yaml(connection, args.defaultsFile)
    transmission_rates = TransmissionRate.load_default_yaml(
        connection_networking.streaming_resolution_per_device[device],
        args.transmissionRatesdefaultsFile,
    )
    modeled_emissions = connection_networking.model_device(device, connection, transmission_rates)

    print(yaml_dump({"networking": modeled_emissions}))


if __name__ == "__main__":
    main()
