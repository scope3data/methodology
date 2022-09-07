#!/usr/bin/env python
""" Compute emissions model for an ad tech company """
import argparse
import logging

import yaml
from utils import get_fact_or_default, get_facts_from_sources, log_result, log_step
from yaml.loader import SafeLoader


class AdTechPlatform:
    """This represents a node in our graph"""

    def __init__(
        self,
        name: str,
        identifier: str,
        primary_bid_request_emissions: float,
        primary_cookie_sync_emissions: float,
        cookie_sync_distribution_rate: float,
        bid_request_rejection_rate: float,
    ) -> None:
        self.name = name
        self.identifier = identifier
        self.primary_bid_request_emissions = primary_bid_request_emissions
        self.primary_cookie_sync_emissions = primary_cookie_sync_emissions
        self.cookie_sync_distribution_rate = cookie_sync_distribution_rate
        self.bid_request_rejection_rate = bid_request_rejection_rate


class DistributionPartner:
    """This represents an edge in our graph"""

    def __init__(
        self,
        partner: AdTechPlatform,
        bid_request_distribution_rate: float,
    ) -> None:
        self.partner = partner
        self.bid_request_distribution_rate = bid_request_distribution_rate


def get_ad_tech_model_keys() -> set[str]:
    return {
        "bid requests processed billion per month",
        "cookie syncs processed billion per month",
        "cookie syncs processed per bid request",
        "cookie sync distribution ratio",
        "creative serving processed billion per month",
        "pct of bid requests processed from ad tech platforms",
        "bid request size in bytes",
        "bid request rejection pct",
        "server to server emissions g per gb",
        "server emissions mt per month",
        "server emissions g per kwh",
        "servers processing bid requests pct",
        "servers processing cookie syncs pct",
        "servers processing creative serving pct",
        "datacenter water intensity h2o m^3 per mwh",
    }


def get_product_info(key: str, default: float | None, product: dict[str, str], depth: int):
    if key in product:
        log_step(key, product[key], "", depth)
        return product[key]
    if default is not None:
        log_step(key, default, "default", depth)
        return default
    raise Exception(
        f"No value found in product {product['name'] if 'name' in product else ''} for '{key}'"
    )


def get_corporate_emissions_per_bid_request(
    corporate_emissions_g: float,
    corporate_allocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    bid_requests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    emissions = corporate_allocation * corporate_emissions_g / bid_requests
    log_result(
        "corporate emissions g per bid request",
        f"{emissions}:.8f",
        depth,
    )
    return emissions


def get_external_request_ratio(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if (
        "ad tech platform bid requests processed billion per month" in facts
        and "bid requests processed billion per month" in facts
    ):
        atp_requests = get_fact_or_default(
            "ad tech platform bid requests processed billion per month",
            facts,
            defaults,
            depth - 1,
        )
        bid_requests = get_fact_or_default(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        ratio = atp_requests / bid_requests
        log_result("external request ratio", f"{ratio * 100.0:.1f}%", depth)
        return ratio
    return (
        get_fact_or_default(
            "pct of bid requests processed from ad tech platforms",
            facts,
            defaults,
            depth,
        )
        / 100
    )


def get_data_transfer_emissions_per_bid_request(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "data transfer emissions mt per month" in facts:
        return get_fact_or_default("data transfer emissions mt per month", facts, defaults, depth)

    external_request_ratio = get_external_request_ratio(facts, defaults, depth - 1)
    bid_request_size_gb = (
        get_fact_or_default("bid request size in bytes", facts, defaults, depth - 1)
        / 1024
        / 1024
        / 1024
    )
    server_to_server_emissions_per_gb = get_fact_or_default(
        "server to server emissions g per gb", facts, defaults, depth - 1
    )
    data_transfer_emissions_per_bid_request = (
        external_request_ratio * bid_request_size_gb * server_to_server_emissions_per_gb
    )

    log_result(
        "data transfer emissions g per bid request",
        f"{data_transfer_emissions_per_bid_request:.8f}",
        depth,
    )
    return data_transfer_emissions_per_bid_request


def get_server_emissions_per_bid_request(
    server_allocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    server_emissions_g = (
        get_fact_or_default("server emissions mt per month", facts, defaults, depth - 1) * 1000000
    )
    bid_requests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    servers_processing_bid_requests = (
        get_fact_or_default("servers processing bid requests pct", facts, defaults, depth - 1)
        / 100.0
    )
    server_emissions_per_bid_request = (
        server_allocation * server_emissions_g * servers_processing_bid_requests / bid_requests
    )
    log_result(
        "server emissions g per bid request",
        f"{server_emissions_per_bid_request:.6f}",
        depth,
    )
    return server_emissions_per_bid_request


def get_primary_emissions_per_bid_request(
    corporate_emissions_per_bid_request: float,
    server_allocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    data_transfer_emissions_per_bid_request = get_data_transfer_emissions_per_bid_request(
        facts, defaults, depth - 1
    )
    server_emissions_per_bid_request = get_server_emissions_per_bid_request(
        server_allocation, facts, defaults, depth - 1
    )
    primary_emissions_per_bid_request = (
        corporate_emissions_per_bid_request
        + data_transfer_emissions_per_bid_request
        + server_emissions_per_bid_request
    )
    log_result(
        "primary emissions mt per billion bid requests",
        f"{primary_emissions_per_bid_request:.6f}",
        depth,
    )
    return primary_emissions_per_bid_request


def get_secondary_emissions_per_bid_request(
    model: AdTechPlatform, distribution_partners: list[DistributionPartner], depth: int
) -> float:
    secondary_emissions_per_bid_request = 0.0
    for edge in distribution_partners:
        secondary_emissions_per_bid_request += (
            edge.partner.primary_bid_request_emissions * edge.bid_request_distribution_rate
        )
    secondary_emissions_per_bid_request *= 1 - model.bid_request_rejection_rate
    log_result("secondary emissions g per bid request", secondary_emissions_per_bid_request, depth)
    return secondary_emissions_per_bid_request


def get_cookie_syncs_processed(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "cookie syncs processed billion per month" in facts:
        return (
            get_fact_or_default("cookie syncs processed billion per month", facts, defaults, depth)
            * 1000000000
        )
    cookie_syncs_per_bid_request = get_fact_or_default(
        "cookie syncs processed per bid request", facts, defaults, depth - 1
    )
    bid_requests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    cookie_syncs_processed = bid_requests * cookie_syncs_per_bid_request
    log_result("cookie syncs processed per month", cookie_syncs_processed, depth)
    return cookie_syncs_processed


def get_water_usage_to_emissions_ratio(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    water_per_m_wh = get_fact_or_default(
        "datacenter water intensity h2o m^3 per mwh", facts, defaults, depth - 1
    )
    emissions_per_k_wh = get_fact_or_default(
        "server emissions g per kwh", facts, defaults, depth - 1
    )
    water_m3_per_emissions_g = water_per_m_wh / emissions_per_k_wh / 1000
    log_result("h2o m^3 per g emissions", water_m3_per_emissions_g, depth)
    return water_m3_per_emissions_g


def get_primary_emissions_per_cookie_sync(
    server_allocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    server_emissions_g = (
        get_fact_or_default("server emissions mt per month", facts, defaults, depth - 1) * 1000000
    )
    requests = get_cookie_syncs_processed(facts, defaults, depth - 1)
    servers_processing_cookie_syncs = (
        get_fact_or_default("servers processing cookie syncs pct", facts, defaults, depth - 1)
        / 100.0
    )
    primary_emissions_per_cookie_sync = (
        server_allocation * server_emissions_g * servers_processing_cookie_syncs / requests
    )
    log_result("primary emissions g per cookie sync", primary_emissions_per_cookie_sync, depth)
    water_usage_to_emissions_ratio = get_water_usage_to_emissions_ratio(facts, defaults, depth - 1)
    primary_water_usage = primary_emissions_per_cookie_sync * water_usage_to_emissions_ratio
    log_result("primary water usage m^3 per cookie sync", primary_water_usage, depth)
    return primary_water_usage


def get_secondary_emissions_per_cookie_sync(
    model: AdTechPlatform, distribution_partners: list[DistributionPartner], depth: int
) -> float:
    secondary_emissions_per_cookie_sync = 0.0
    for edge in distribution_partners:
        secondary_emissions_per_cookie_sync += edge.partner.primary_cookie_sync_emissions
    secondary_emissions_per_cookie_sync *= model.cookie_sync_distribution_rate
    log_result(
        "secondary emissions g per cookie sync",
        f"{secondary_emissions_per_cookie_sync:.6f}",
        depth,
    )
    return secondary_emissions_per_cookie_sync


def process_product(
    product: dict[str, str],
    facts: dict[str, float],
    defaults_document: dict[str, dict[str, dict[str, float]]],
    corporate_emissions_g: float | None,
    corporate_emissions_g_per_imp: float | None,
    depth: int,
) -> AdTechPlatform:
    if "name" not in product:
        raise Exception("No 'name' field found in a product")

    logging.info(f"#### {product['name']}")
    template = get_product_info("template", None, product, 0)
    identifier = get_product_info("identifier", None, product, 0)
    server_allocation = get_product_info("server allocation pct", 100, product, 0) / 100
    corporate_allocation = get_product_info("corporate allocation pct", 100, product, 0) / 100
    if template not in defaults_document["defaults"]:
        raise Exception(f"Template {template} not found in defaults")
    defaults = defaults_document["defaults"][template]

    corporate_emissions_per_bid_request = corporate_emissions_g_per_imp
    if corporate_emissions_g:
        corporate_emissions_per_bid_request = get_corporate_emissions_per_bid_request(
            corporate_emissions_g, corporate_allocation, facts, defaults, depth - 1
        )

    if not corporate_emissions_per_bid_request:
        raise Exception("failed to compute corporate emissions per bid request")

    primary_emissions_per_bid_request = get_primary_emissions_per_bid_request(
        corporate_emissions_per_bid_request, server_allocation, facts, defaults, depth
    )
    primary_emissions_per_cookie_sync = get_primary_emissions_per_cookie_sync(
        server_allocation, facts, defaults, depth
    )
    cookie_sync_distribution_ratio = get_fact_or_default(
        "cookie sync distribution ratio", facts, defaults, depth - 1
    )
    bid_request_rejection_rate = (
        get_fact_or_default("bid request rejection pct", facts, defaults, depth - 1) / 100.0
    )
    model = AdTechPlatform(
        str(product["name"]),
        identifier,
        primary_emissions_per_bid_request,
        primary_emissions_per_cookie_sync,
        cookie_sync_distribution_ratio,
        bid_request_rejection_rate,
    )
    return model


def main():

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
        help="Provide the corporate emissionsfor organization",
    )
    parser.add_argument(
        "--corporateEmissionsGPerImp",
        const=1,
        type=float,
        nargs="?",
        help="Provide the corporate emissions for organization per bid request",
    )
    parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Load defaults
    defaults_stream = open(args.defaultsFile, "r")
    defaults_document = yaml.load(defaults_stream, Loader=SafeLoader)

    # Load facts about the company
    stream = open(args.companyFile[0], "r")
    document = yaml.load(stream, Loader=SafeLoader)
    if "company" not in document:
        raise Exception("No 'company' field found in company file")
    if "products" not in document["company"]:
        raise Exception("No 'products' field found in company file")
    if "sources" not in document["company"]:
        raise Exception("No 'sources' field found in company file")
    facts = get_facts_from_sources(document["company"]["sources"])

    corporate_emissions_g = args.corporateEmissionsG
    corporate_emissions_g_per_imp = args.corporateEmissionsGPerImp

    if not corporate_emissions_g and not corporate_emissions_g_per_imp:
        raise Exception("Must provide either --corporateEmissionsG or --corporateEmissionsGPerImp")

    depth = 4 if args.verbose else 0
    product_models = []
    for product in document["company"]["products"]:
        model = process_product(
            product,
            facts,
            defaults_document,
            corporate_emissions_g,
            corporate_emissions_g_per_imp,
            depth,
        )
        product_models.append(model)

    print(yaml.dump({"products": product_models}, Dumper=yaml.Dumper))

    if args.partners and args.verbose:
        distribution_partners: list[DistributionPartner] = []
        for i in range(args.partners):
            partner = AdTechPlatform(f"dummy {i}", f"dummy{i}.com", 0.001, 0.0001, 1.0, 0.3)
            distribution_partners.append(DistributionPartner(partner, 1.0))

        get_secondary_emissions_per_bid_request(product_models[0], distribution_partners, depth - 1)
        get_secondary_emissions_per_cookie_sync(product_models[0], distribution_partners, depth - 1)


if __name__ == "__main__":
    main()
