#!/usr/bin/env python
""" Compute emissions for a end user device emissions for a specific property channel """
import argparse
import logging

from scope3_methodology.end_user_device.model import EndUserDevice
from scope3_methodology.publisher.model import Property
from scope3_methodology.utils.yaml_helpers import yaml_dump


def parse_args():
    """Parse the command line arguments"""
    # arse command line to get company file
    parser = argparse.ArgumentParser(description="Compute emissions for an end user device")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="end_user_device-defaults.yaml",
        help="Set the end user device defaults file to use",
    )
    parser.add_argument(
        "-p",
        "--propertyDefaultsFile",
        default="property-defaults.yaml",
        help="Set the property defaults file to use",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
    parser.add_argument("channel", nargs=1, help="The channel the device is being used within ")
    parser.add_argument(
        "device",
        nargs=1,
        help="Environment to model: personal_computer, smartphone, tablet, tv_system",
    )

    return parser.parse_args()


def main():
    """Model the emisisons for an end user device for specific property channel"""
    # Process Command Line Arguments
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    template = "generic"
    channel = str(args.channel[0]).lower()
    device = str(args.device[0])
    property_defaults = Property.load_default_yaml(template, args.propertyDefaultsFile, channel)

    if not property_defaults.quality_impressions_per_duration_s:
        logging.error("Unable to compute end user device emissions for channel: %s", channel)
        return

    unmodeled_end_user_device = EndUserDevice.load_default_yaml(device, args.defaultsFile)
    modeled_end_user_device = unmodeled_end_user_device.model_end_user_device(
        device,
        channel,
        template,
        property_defaults.quality_impressions_per_duration_s,
    )
    if modeled_end_user_device is not None:
        print(yaml_dump({device: modeled_end_user_device}))


if __name__ == "__main__":
    main()
