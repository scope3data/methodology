#!/usr/bin/env python
""" Compute corporate emissions for an organization """
import argparse
import json
import logging

import yaml
from utils import get_fact_or_default, get_facts_from_sources, log_result
from yaml.loader import SafeLoader


def get_corporate_keys() -> set[str]:
    return {
        "corporate emissions mt per month",
        "office emissions mt per employee per month",
        "travel emissions mt per employee per month",
        "overhead emissions mt per employee per month",
        "commuting emissions mt per employee per month",
        "datacenter emissions mt per employee per month",
    }


def compute_emissions(facts: dict[str, float], defaults: dict[str, float], depth: int) -> float:
    if "corporate emissions mt per month" in facts:
        return get_fact_or_default("corporate emissions mt per month", facts, defaults, depth)
    if "employees" not in facts:
        raise Exception("Must provide either 'corporate emissions mt per month' or 'employees'")
    office_emissions_per_employee = get_fact_or_default(
        "office emissions mt per employee per month", facts, defaults, depth - 1
    )
    travel_emissions_per_employee = get_fact_or_default(
        "travel emissions mt per employee per month", facts, defaults, depth - 1
    )
    datacenter_emissions_per_employee = get_fact_or_default(
        "datacenter emissions mt per employee per month", facts, defaults, depth - 1
    )
    commuting_emissions_per_employee = get_fact_or_default(
        "commuting emissions mt per employee per month", facts, defaults, depth - 1
    )
    overhead_emissions_per_employee = get_fact_or_default(
        "overhead emissions mt per employee per month", facts, defaults, depth - 1
    )
    corporate_emissions = get_fact_or_default("employees", facts, defaults, depth - 1) * (
        office_emissions_per_employee
        + travel_emissions_per_employee
        + commuting_emissions_per_employee
        + datacenter_emissions_per_employee
        + overhead_emissions_per_employee
    )
    log_result("corporate emissions mt per month", f"{corporate_emissions:.2f}", depth)
    return corporate_emissions


def main():
    # Parse command line to get company file
    parser = argparse.ArgumentParser(description="Compute corporate emissions")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="organization-defaults.yaml",
        help="Set the defaults file to use (overrides organization-defaults.yaml)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
    parser.add_argument("--companyFile", help="The company file to parse in YAML format")
    parser.add_argument(
        "-p",
        "--publisher",
        const=1,
        default=False,
        type=bool,
        nargs="?",
        help="Whether to compute corporate emissions as if the company is a publisher",
    )
    parser.add_argument(
        "-a",
        "--adTechPlatform",
        const=1,
        default=False,
        type=bool,
        nargs="?",
        help="Whether to compute corporate emissions as if the company is a ad tech platform",
    )
    parser.add_argument(
        "-o",
        "--outputFilename",
        const=1,
        type=str,
        nargs="?",
    )
    parser.add_argument(
        "--corporateEmissionFacts",
        const=1,
        type=str,
        nargs="?",
    )

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Load defaults
    defaults_stream = open(args.defaultsFile, "r")
    defaults_document = yaml.load(defaults_stream, Loader=SafeLoader)

    # Load facts about the company
    if not args.companyFile and not args.corporateEmissionFacts:
        raise Exception("Must provide either --companyFile or --corporateEmissionFacts")

    facts = {}
    if args.companyFile:
        print(args.companyFile)
        stream = open(args.companyFile, "r")
        document = yaml.load(stream, Loader=SafeLoader)
        if "company" not in document:
            raise Exception("No 'company' field found in company file")
        if "products" not in document["company"]:
            raise Exception("No 'products' field found in company file")
        if "sources" not in document["company"]:
            raise Exception("No 'sources' field found in company file")
        facts = get_facts_from_sources(document["company"]["sources"])
    else:
        facts = json.loads(args.corporateEmissionFacts)

    depth = 4 if args.verbose else 0
    org_emissions = {}
    if args.publisher:
        defaults = defaults_document["defaults"]["publisher"]
        org_emissions["publisher"] = compute_emissions(facts, defaults, depth - 1) * 1000000
    if args.adTechPlatform:
        defaults = defaults_document["defaults"]["adTechPlatform"]
        org_emissions["adTechPlatform"] = compute_emissions(facts, defaults, depth - 1) * 1000000

    output = yaml.dump({"corporateEmissions": org_emissions}, Dumper=yaml.Dumper)
    if args.outputFilename:
        write_stream = open(args.outputFilename, "w")
        write_stream.write(output)
        write_stream.close()
    else:
        print(output)


if __name__ == "__main__":
    main()
