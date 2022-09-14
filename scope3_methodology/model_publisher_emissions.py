#!/usr/bin/env python
""" Compute emissions for a publishers properties """
import argparse
import logging

import yaml
from publisher.model import ModeledProperty, Property
from utils.utils import get_facts


def parse_args():
    """Parse the command line arguments"""
    # arse command line to get company file
    parser = argparse.ArgumentParser(description="Compute emissions for an publisher")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="property-defaults.yaml",
        help="Set the defaults file to use (overrides property-defaults.yaml)",
    )
    parser.add_argument(
        "-e",
        "--environment",
        const=1,
        default="computer",
        type=str,
        nargs="?",
        help="Environment to model: computer, mobile, tv",
    )
    parser.add_argument(
        "-b",
        "--buying-method",
        const=1,
        default="programmatic",
        type=str,
        nargs="?",
        help="Buying mechanism to model: guaranteed, programmatic, native",
    )
    parser.add_argument(
        "-g",
        "--gridIntensity",
        const=1,
        default=539,
        type=int,
        nargs="?",
        help="Carbon intensity of the energy grid in g co2e per KWh",
    )
    parser.add_argument(
        "-p",
        "--partners",
        const=1,
        default=10,
        type=int,
        nargs="?",
        help="Simulate ad tech partners",
    )
    parser.add_argument(
        "-a",
        "--auctions",
        const=1,
        default=2,
        type=int,
        nargs="?",
        help="Simulate multiple auctions",
    )
    parser.add_argument(
        "--corporateEmissionsG",
        const=1,
        type=float,
        nargs="?",
        help="Provide the corporate emissions for organization",
    )
    parser.add_argument(
        "--corporateEmissionsGPerImp",
        const=1,
        type=float,
        nargs="?",
        help="Provide the corporate emissions for organization per impression",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
    parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")

    return parser.parse_args()


def process_property(
    publisher_property: dict[str, str],
    defaults_file: str,
    depth: int,
    grid_intensity_g_co2e_per_kwh: float,
    environment: str,
) -> ModeledProperty:
    """
    Process a single publisher property.
    :return: ModeledProperty
    """
    # Validate property & get property facts
    if "identifier" not in publisher_property or "template" not in publisher_property:
        raise Exception("Each property must have an identifier and a template")
    template = publisher_property["template"]
    facts = get_facts(publisher_property["facts"])

    # Add in additional facts not parsed from yaml
    facts["environment"] = environment
    facts["grid_intensity_g_co2e_per_kwh"] = grid_intensity_g_co2e_per_kwh
    unmodeled_property = Property(**facts)
    defaults = Property.load_default_yaml(template, defaults_file)
    return unmodeled_property.model_property(publisher_property["identifier"], defaults, depth)


def main():
    """Model the emisisons for a publishers properties"""
    # Process Command Line Arguments
    args = parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Load facts about the company
    with open(args.companyFile[0], "r") as stream:
        document = yaml.safe_load(stream)
        if "properties" not in document:
            raise Exception("No 'properties' field found in company file")

        depth = 4 if args.verbose else 0

        publisher_impressions = 0.0
        properties: list[Property] = []
        for publisher_property in document["properties"]:
            modeled_property = process_property(
                publisher_property=publisher_property,
                defaults_file=args.defaultsFile,
                grid_intensity_g_co2e_per_kwh=args.gridIntensity,
                environment=args.environment,
                depth=depth,
            )
            publisher_impressions += modeled_property.impressions
            properties.append(modeled_property)

    # By default when processing the property the default corproate emissions g per impression
    # is set, only if we have direct inputs will we then override this values
    if args.corporateEmissionsG or args.corporateEmissionsGPerImp:
        corporate_emissions_g = args.corporateEmissionsG
        corporate_emissions_g_per_imp = args.corporateEmissionsGPerImp
        for modeled_property in properties:
            if corporate_emissions_g:
                modeled_property.set_corporate_emissions_g_co2e_per_impression(
                    corporate_emissions_g * modeled_property.impressions / publisher_impressions,
                    None,
                )
            else:
                modeled_property.set_corporate_emissions_g_co2e_per_impression(
                    None, corporate_emissions_g_per_imp
                )

    print(yaml.dump({"properties": properties}, Dumper=yaml.Dumper))


if __name__ == "__main__":
    main()
