#!/usr/bin/env python
""" Compute emissions model for an ad tech company """
import argparse
import logging

import yaml
from corporate import get_corporate_emissions
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


# Parse command line to get company file
parser = argparse.ArgumentParser(description="Compute emissions for an ad tech company")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to use (overrides defaults.yaml)",
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
parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.INFO)

# Load defaults
defaultsStream = open(args.defaultsFile, "r")
defaultsDocument = yaml.load(defaultsStream, Loader=SafeLoader)

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


def getProductInfo(key: str, default: float | None, product: dict[str, float], depth: int):
    if key in product:
        log_step(key, product[key], "", depth)
        return product[key]
    if default is not None:
        log_step(key, default, "default", depth)
        return default
    raise Exception(
        f"No value found in product {product['name'] if 'name' in product else ''} for '{key}'"
    )


def getCorporateEmissionsPerBidRequest(
    corporateAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    corporateEmissionsG = get_corporate_emissions(facts, defaults, depth - 1) * 1000000
    bidRequests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    corporateEmissionsPerBidRequest = corporateAllocation * corporateEmissionsG / bidRequests
    log_result(
        "corporate emissions g per bid request",
        f"{corporateEmissionsPerBidRequest}:.8f",
        depth,
    )
    return corporateEmissionsPerBidRequest


def getExternalRequestRatio(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if (
        "ad tech platform bid requests processed billion per month" in facts
        and "bid requests processed billion per month" in facts
    ):
        atpRequests = get_fact_or_default(
            "ad tech platform bid requests processed billion per month",
            facts,
            defaults,
            depth - 1,
        )
        bidRequests = get_fact_or_default(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        ratio = atpRequests / bidRequests
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


def getDataTransferEmissionsPerBidRequest(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "data transfer emissions mt per month" in facts:
        return get_fact_or_default("data transfer emissions mt per month", facts, defaults, depth)

    externalRequestRatio = getExternalRequestRatio(facts, defaults, depth - 1)
    bidRequestSizeGB = (
        get_fact_or_default("bid request size in bytes", facts, defaults, depth - 1)
        / 1024
        / 1024
        / 1024
    )
    serverToServerEmissionsPerGB = get_fact_or_default(
        "server to server emissions g per gb", facts, defaults, depth - 1
    )
    dataTransferEmissionsPerBidRequest = (
        externalRequestRatio * bidRequestSizeGB * serverToServerEmissionsPerGB
    )

    log_result(
        "data transfer emissions g per bid request",
        f"{dataTransferEmissionsPerBidRequest:.8f}",
        depth,
    )
    return dataTransferEmissionsPerBidRequest


def getServerEmissionsPerBidRequest(
    serverAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    serverEmissionsG = (
        get_fact_or_default("server emissions mt per month", facts, defaults, depth - 1) * 1000000
    )
    bidRequests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    serversProcessingBidRequests = (
        get_fact_or_default("servers processing bid requests pct", facts, defaults, depth - 1)
        / 100.0
    )
    serverEmissionsPerBidRequest = (
        serverAllocation * serverEmissionsG * serversProcessingBidRequests / bidRequests
    )
    log_result(
        "server emissions g per bid request",
        f"{serverEmissionsPerBidRequest:.6f}",
        depth,
    )
    return serverEmissionsPerBidRequest


def getPrimaryEmissionsPerBidRequest(
    serverAllocation: float,
    corporateAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    corporateEmissionsPerBidRequest = getCorporateEmissionsPerBidRequest(
        corporateAllocation, facts, defaults, depth - 1
    )
    dataTransferEmissionsPerBidRequest = getDataTransferEmissionsPerBidRequest(
        facts, defaults, depth - 1
    )
    serverEmissionsPerBidRequest = getServerEmissionsPerBidRequest(
        serverAllocation, facts, defaults, depth - 1
    )
    primaryEmissionsPerBidRequest = (
        corporateEmissionsPerBidRequest
        + dataTransferEmissionsPerBidRequest
        + serverEmissionsPerBidRequest
    )
    log_result(
        "primary emissions mt per billion bid requests",
        f"{primaryEmissionsPerBidRequest:.6f}",
        depth,
    )
    return primaryEmissionsPerBidRequest


def getSecondaryEmissionsPerBidRequest(
    model: AdTechPlatform,
    distributionPartners: list[DistributionPartner],
) -> float:
    secondaryEmissionsPerBidRequest = 0.0
    for edge in distributionPartners:
        secondaryEmissionsPerBidRequest += (
            edge.partner.primary_bid_request_emissions * edge.bid_request_distribution_rate
        )
    secondaryEmissionsPerBidRequest *= 1 - model.bid_request_rejection_rate
    log_result("secondary emissions g per bid request", secondaryEmissionsPerBidRequest, depth)
    return secondaryEmissionsPerBidRequest


def getCookieSyncsProcessed(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "cookie syncs processed billion per month" in facts:
        return (
            get_fact_or_default("cookie syncs processed billion per month", facts, defaults, depth)
            * 1000000000
        )
    cookieSyncsPerBidRequest = get_fact_or_default(
        "cookie syncs processed per bid request", facts, defaults, depth - 1
    )
    bidRequests = (
        get_fact_or_default("bid requests processed billion per month", facts, defaults, depth - 1)
        * 1000000000
    )
    cookieSyncsProcessed = bidRequests * cookieSyncsPerBidRequest
    log_result("cookie syncs processed per month", cookieSyncsProcessed, depth)
    return cookieSyncsProcessed


def getWaterUsageToEmissionsRatio(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    waterPerMWh = get_fact_or_default(
        "datacenter water intensity h2o m^3 per mwh", facts, defaults, depth - 1
    )
    emissionsPerKWh = get_fact_or_default("server emissions g per kwh", facts, defaults, depth - 1)
    waterM3PerEmissionsG = waterPerMWh / emissionsPerKWh / 1000
    log_result("h2o m^3 per g emissions", waterM3PerEmissionsG, depth)
    return waterM3PerEmissionsG


def getPrimaryEmissionsPerCookieSync(
    serverAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    serverEmissionsG = (
        get_fact_or_default("server emissions mt per month", facts, defaults, depth - 1) * 1000000
    )
    cookieSyncRequests = getCookieSyncsProcessed(facts, defaults, depth - 1)
    serversProcessingCookieSyncs = (
        get_fact_or_default("servers processing cookie syncs pct", facts, defaults, depth - 1)
        / 100.0
    )
    primaryEmissionsPerCookieSync = (
        serverAllocation * serverEmissionsG * serversProcessingCookieSyncs / cookieSyncRequests
    )
    log_result("primary emissions g per cookie sync", primaryEmissionsPerCookieSync, depth)
    waterUsageToEmissionsRatio = getWaterUsageToEmissionsRatio(facts, defaults, depth - 1)
    primaryWaterUsagePerCookieSync = primaryEmissionsPerCookieSync * waterUsageToEmissionsRatio
    log_result("primary water usage m^3 per cookie sync", primaryWaterUsagePerCookieSync, depth)
    return primaryEmissionsPerCookieSync


def getSecondaryEmissionsPerCookieSync(
    model: AdTechPlatform, distributionPartners: list[DistributionPartner]
) -> float:
    secondary_emissions_per_cookie_sync = 0.0
    for edge in distributionPartners:
        secondary_emissions_per_cookie_sync += edge.partner.primary_cookie_sync_emissions
    secondary_emissions_per_cookie_sync *= model.cookie_sync_distribution_rate
    log_result(
        "secondary emissions g per cookie sync",
        f"{secondary_emissions_per_cookie_sync:.6f}",
        depth,
    )
    return secondary_emissions_per_cookie_sync


depth = 4 if args.verbose else 0
productModels = []
for product in document["company"]["products"]:
    if "name" not in product:
        raise Exception(f"No 'name' field found in a product")

    logging.info(f"#### {product['name']}")
    template = getProductInfo("template", None, product, 0)
    identifier = getProductInfo("identifier", None, product, 0)
    serverAllocation = getProductInfo("server allocation pct", 100, product, 0) / 100
    corporateAllocation = getProductInfo("corporate allocation pct", 100, product, 0) / 100
    if template not in defaultsDocument["defaults"]:
        raise Exception(f"Template {template} not found in defaults")
    defaults = defaultsDocument["defaults"][template]
    primaryEmissionsPerBidRequest = getPrimaryEmissionsPerBidRequest(
        serverAllocation, corporateAllocation, facts, defaults, depth
    )
    primaryEmissionsPerCookieSync = getPrimaryEmissionsPerCookieSync(
        serverAllocation, facts, defaults, depth
    )
    cookieSyncDistributionRatio = get_fact_or_default(
        "cookie sync distribution ratio", facts, defaults, depth - 1
    )
    bidRequestRejectionRate = (
        get_fact_or_default("bid request rejection pct", facts, defaults, depth - 1) / 100.0
    )
    model = AdTechPlatform(
        product["name"],
        identifier,
        primaryEmissionsPerBidRequest,
        primaryEmissionsPerCookieSync,
        cookieSyncDistributionRatio,
        bidRequestRejectionRate,
    )
    productModels.append(model)

print(yaml.dump({"products": productModels}, Dumper=yaml.Dumper))

if args.partners and args.verbose:
    distributionPartners: list[DistributionPartner] = []
    for i in range(args.partners):
        partner = AdTechPlatform(f"dummy {i}", f"dummy{i}.com", 0.001, 0.0001, 1.0, 0.3)
        distributionPartners.append(DistributionPartner(partner, 1.0))

    getSecondaryEmissionsPerBidRequest(productModels[0], distributionPartners)
    getSecondaryEmissionsPerCookieSync(productModels[0], distributionPartners)
