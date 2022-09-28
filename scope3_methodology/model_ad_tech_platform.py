#!/usr/bin/env python
""" Compute emissions model for an ad tech company """
import argparse
import logging

import yaml
from ad_tech_platform.helpers import get_product_info
from ad_tech_platform.model import (
    AdTechPlatform,
    DistributionPartner,
    ModeledAdTechPlatform,
)
from utils.utils import get_facts


def parse_args():
    """Parse the command line arguments"""
    # Parse command line to get company file
    parser = argparse.ArgumentParser(description="Compute emissions for an ad tech company")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="atp-defaults.yaml",
        help="Set the defaults file to use (overrides atp-defaults.yaml)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
    parser.add_argument(
        "-p",
        "--partners",
        const=1,
        default=0,
        type=int,
        nargs="?",
        help="Simulate distribution partners",
    )
    parser.add_argument(
        "--corporateEmissionsG",
        const=1,
        type=float,
        nargs="?",
        help="""
            Provide the corporate emissions for organization.
            If not provided will fallback to default corporate_emissions_g_co2e_per_bid_request
            """,
    )
    parser.add_argument(
        "--corporateEmissionsGPerBidRequest",
        const=1,
        type=float,
        nargs="?",
        help="""
            Provide the corporate emissions for organization per bid request.
            If not provided will fallback to default corporate_emissions_g_co2e_per_bid_request
            """,
    )
    parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
    return parser.parse_args()


def process_product(
    product: dict[str, str],
    defaults_file: str,
    depth: int,
    distribution_partners: list[DistributionPartner],
    corporate_emissions_g: float | None = None,
    corporate_emissions_g_per_bid_request: float | None = None,
) -> ModeledAdTechPlatform:
    """
    Model the product (atp)
    :return: ModeledAdTechPlatform
    """
    # Validate product
    if "name" not in product:
        raise Exception("No 'name' field found in a product")

    name = product["name"]
    logging.info(f"#### {name}")
    template = get_product_info("template", None, product, 0)
    identifier = get_product_info("identifier", None, product, 0)
    facts = get_facts(product["facts"]) if "facts" in product else {}

    facts["allocation_of_company_servers_pct"] = get_product_info(
        "allocation_of_company_servers_pct", 100, product, 0
    )
    facts["allocation_of_corporate_emissions_pct"] = get_product_info(
        "allocation_of_corporate_emissions_pct", 100, product, 0
    )
    atp = AdTechPlatform(**facts)
    defaults = AdTechPlatform.load_default_yaml(template, defaults_file)
    modeled_product = atp.model_product(
        name=name,
        identifier=identifier,
        defaults=defaults,
        distribution_partners=distribution_partners,
        corporate_emissions_g=corporate_emissions_g,
        corporate_emissions_g_per_bid_request=corporate_emissions_g_per_bid_request,
        depth=depth,
    )
    return modeled_product


def main():
    """Model the emissions for a ad tech platform"""
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Load facts about the company
    with open(args.companyFile[0], "r") as stream:
        document = yaml.safe_load(stream)
        if "products" not in document:
            raise Exception("No 'products' field found in company file")

        # If neither is provided, we will fallback to default corp emissions per bid request
        corporate_emissions_g = args.corporateEmissionsG
        corporate_emissions_g_per_bid_request = args.corporateEmissionsGPerBidRequest

        distribution_partners: list[DistributionPartner] = []
        if args.partners and args.verbose:
            for i in range(args.partners):
                partner = ModeledAdTechPlatform(
                    name=f"dummy {i}",
                    identifier=f"dummy{i}.com",
                    primary_bid_request_emissions_g_co2e=0.00020403552546744037,
                    primary_cookie_sync_emissions_g_co2e=0.00035312100449136157,
                    cookie_sync_distribution_ratio=1.0,
                    atp_block_rate=0.0,
                )
                distribution_partners.append(DistributionPartner(partner, 1.0))

        depth = 4 if args.verbose else 0
        product_models = []
        for product in document["products"]:
            modeled_product = process_product(
                product=product,
                defaults_file=args.defaultsFile,
                corporate_emissions_g=corporate_emissions_g,
                corporate_emissions_g_per_bid_request=corporate_emissions_g_per_bid_request,
                depth=depth,
                distribution_partners=distribution_partners,
            )
            product_models.append(modeled_product)

    print(yaml.dump({"products": product_models}, Dumper=yaml.Dumper))


if __name__ == "__main__":
    main()
