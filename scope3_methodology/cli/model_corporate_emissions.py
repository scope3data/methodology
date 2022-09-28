#!/usr/bin/env python
""" Compute corporate emissions for an organization """
import argparse
import logging

import yaml

from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.utils.utils import get_facts


def main():
    """
    Model corporate emissions for a company.
    Must specify the company file and type.
    """
    # Parse command line to get company file
    parser = argparse.ArgumentParser(description="Compute corporate emissions")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="organization-defaults.yaml",
        help="Set the defaults file to use (overrides organization-defaults.yaml)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
    parser.add_argument(
        "type",
        choices=["generic", "publisher", "atp"],
        help="Type of organization for computing defaults",
    )
    parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Load facts about the company
    with open(args.companyFile[0], "r") as stream:
        document = yaml.safe_load(stream)
        if "name" not in document:
            raise Exception("No 'name' field found in company file")
        facts = get_facts(document["facts"]) if "facts" in document else {}

        depth = 4 if args.verbose else 0
        corp = CorporateEmissions(**facts)  # type: ignore
        defaults = CorporateEmissions.load_default_yaml(args.type, args.defaultsFile)
        org_emissions = corp.comp_emissions_g_co2e_per_month(defaults, depth - 1)
    print(yaml.dump({"corporate_emissions_g_co2e_per_month": org_emissions}, Dumper=yaml.Dumper))


if __name__ == "__main__":
    main()
