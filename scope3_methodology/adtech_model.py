#!/usr/bin/env python
import yaml
from yaml.loader import SafeLoader
import argparse

# This represents a node in our graph
class AdTechPlatform:
    def __init__(
        self,
        name: str,
        identifier: str,
        primaryBidRequestEmissions: float,
        primaryCookieSyncEmissions: float,
        cookieSyncDistributionRate: float,
        bidRequestRejectionRate: float,
    ) -> None:
        self.name = name
        self.identifier = identifier
        self.primaryBidRequestEmissions = primaryBidRequestEmissions
        self.primaryCookieSyncEmissions = primaryCookieSyncEmissions
        self.cookieSyncDistributionRate = cookieSyncDistributionRate
        self.bidRequestRejectionRate = bidRequestRejectionRate


# This represents an edge in our graph
class DistributionPartner:
    def __init__(
        self,
        partner: AdTechPlatform,
        bidRequestDistributionRatio: float,
    ) -> None:
        self.partner = partner
        self.bidRequestDistributionRatio = bidRequestDistributionRatio


# Parse command line to get company file
parser = argparse.ArgumentParser(description="Compute emissions for an ad tech company")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to use (overrides defaults.yaml)",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Show derivation of output"
)
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
    "companyFile", nargs=1, help="The company file to parse in YAML format"
)
args = parser.parse_args()

if args.verbose:

    def verboseprint(*args, **kwargs) -> None:
        print(*args, **kwargs)

else:
    verboseprint = lambda *a, **k: None  # do-nothing function

# Load defaults
defaultsStream = open(args.defaultsFile, "r")
defaultsDocument = yaml.load(defaultsStream, Loader=SafeLoader)

# Load facts about the company
facts: dict[str, float] = {}
stream = open(args.companyFile[0], "r")
documents = list(yaml.load_all(stream, Loader=SafeLoader))
template: str
document = documents[0]  # shouldn't have multiple
if "company" not in document:
    raise Exception("No 'company' field found in company file")
if "products" not in document["company"]:
    raise Exception("No 'products' field found in company file")
if "sources" not in document["company"]:
    raise Exception("No 'sources' field found in company file")
for source in document["company"]["sources"]:
    for fact in source["source"]["facts"]:
        keys = [key for key in fact["fact"] if key != "reference" and key != "comment"]
        for key in keys:
            facts[key] = fact["fact"][key]


def getProductInfo(
    key: str, default: float | None, product: dict[str, float], depth: int
):
    if key in product:
        verboseprint(f"{'  ' * depth}{key} = {product[key]}")
        return product[key]
    if default is not None:
        verboseprint(f"{'  ' * depth}{key} = {default} (default)")
        return default
    raise Exception(
        f"No value found in product {product['name'] if 'name' in product else ''} for '{key}'"
    )


def getFactOrDefault(
    key: str, facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if key in facts:
        verboseprint(f"{'  ' * depth}{key} = {facts[key]}")
        return facts[key]
    if key in defaults:
        verboseprint(f"{'  ' * depth}{key} = {defaults[key]} (default)")
        return defaults[key]
    raise Exception(f"No default found for '{key}'")


def getCorporateEmissions(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "corporate emissions mt per month" in facts:
        return getFactOrDefault(
            "corporate emissions mt per month", facts, defaults, depth
        )
    if not "employees" in facts:
        raise Exception(
            "Must provide either 'corporate emissions mt per month' or 'employees'"
        )
    officeEmissionsPerEmployee = getFactOrDefault(
        "office emissions mt per employee per month", facts, defaults, depth - 1
    )
    travelEmissionsPerEmployee = getFactOrDefault(
        "travel emissions mt per employee per month", facts, defaults, depth - 1
    )
    itEmissionsPerEmployee = getFactOrDefault(
        "it emissions mt per employee per month", facts, defaults, depth - 1
    )
    commutingEmissionsPerEmployee = getFactOrDefault(
        "commuting emissions mt per employee per month", facts, defaults, depth - 1
    )
    corporateEmissions = getFactOrDefault("employees", facts, defaults, depth - 1) * (
        officeEmissionsPerEmployee
        + travelEmissionsPerEmployee
        + commutingEmissionsPerEmployee
        + itEmissionsPerEmployee
    )
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}corporate emissions mt per month: {corporateEmissions:.2f} (calculation)"
    )
    return corporateEmissions


def getCorporateEmissionsPerBidRequest(
    corporateAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    corporateEmissionsG = getCorporateEmissions(facts, defaults, depth - 1) * 1000000
    bidRequests = (
        getFactOrDefault(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        * 1000000000
    )
    corporateEmissionsPerBidRequest = (
        corporateAllocation * corporateEmissionsG / bidRequests
    )
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}corporate emissions g per bid request: {corporateEmissionsPerBidRequest:.8f} (calculation)"
    )
    return corporateEmissionsPerBidRequest


def getExternalRequestRatio(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if (
        "ad tech platform bid requests processed billion per month" in facts
        and "bid requests processed billion per month" in facts
    ):
        atpRequests = getFactOrDefault(
            "ad tech platform bid requests processed billion per month",
            facts,
            defaults,
            depth - 1,
        )
        bidRequests = getFactOrDefault(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        ratio = atpRequests / bidRequests
        verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
        verboseprint(
            f"{'  ' * depth}external request ratio: {ratio * 100.0:.1f}% (calculation)"
        )
        return ratio
    return (
        getFactOrDefault(
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
        return getFactOrDefault(
            "data transfer emissions mt per month", facts, defaults, depth
        )

    externalRequestRatio = getExternalRequestRatio(facts, defaults, depth - 1)
    bidRequestSizeGB = (
        getFactOrDefault("bid request size in bytes", facts, defaults, depth - 1)
        / 1024
        / 1024
        / 1024
    )
    serverToServerEmissionsPerGB = getFactOrDefault(
        "server to server emissions g per gb", facts, defaults, depth - 1
    )
    dataTransferEmissionsPerBidRequest = (
        externalRequestRatio * bidRequestSizeGB * serverToServerEmissionsPerGB
    )

    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}data transfer emissions g per bid request: {dataTransferEmissionsPerBidRequest:.8f} (calculation)"
    )
    return dataTransferEmissionsPerBidRequest


def getServerEmissionsPerBidRequest(
    serverAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    serverEmissionsG = (
        getFactOrDefault("server emissions mt per month", facts, defaults, depth - 1)
        * 1000000
    )
    bidRequests = (
        getFactOrDefault(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        * 1000000000
    )
    serversProcessingBidRequests = (
        getFactOrDefault(
            "servers processing bid requests pct", facts, defaults, depth - 1
        )
        / 100.0
    )
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    serverEmissionsPerBidRequest = (
        serverAllocation * serverEmissionsG * serversProcessingBidRequests / bidRequests
    )
    verboseprint(
        f"{'  ' * depth}server emissions g per bid request: {serverEmissionsPerBidRequest:.6f} (calculation)"
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
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    primaryEmissionsPerBidRequest = (
        corporateEmissionsPerBidRequest
        + dataTransferEmissionsPerBidRequest
        + serverEmissionsPerBidRequest
    )
    verboseprint(
        f"{'  ' * depth}primary emissions mt per billion bid requests: {primaryEmissionsPerBidRequest:.6f} (calculation)"
    )
    return primaryEmissionsPerBidRequest


def getSecondaryEmissionsPerBidRequest(
    model: AdTechPlatform,
    distributionPartners: list[DistributionPartner],
) -> float:
    secondaryEmissionsPerBidRequest = 0.0
    for edge in distributionPartners:
        secondaryEmissionsPerBidRequest += (
            edge.partner.primaryBidRequestEmissions * edge.bidRequestDistributionRatio
        )
    secondaryEmissionsPerBidRequest *= 1 - model.bidRequestRejectionRate
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}secondary emissions g per bid request: {secondaryEmissionsPerBidRequest} (calculation using {len(distributionPartners)} partners)"
    )
    return secondaryEmissionsPerBidRequest


def getCookieSyncsProcessed(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "cookie syncs processed billion per month" in facts:
        return (
            getFactOrDefault(
                "cookie syncs processed billion per month", facts, defaults, depth
            )
            * 1000000000
        )
    cookieSyncsPerBidRequest = getFactOrDefault(
        "cookie syncs processed per bid request", facts, defaults, depth - 1
    )
    bidRequests = (
        getFactOrDefault(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        * 1000000000
    )
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    cookieSyncsProcessed = bidRequests * cookieSyncsPerBidRequest
    verboseprint(
        f"{'  ' * depth}cookie syncs processed per month: {cookieSyncsProcessed} (calculation)"
    )
    return cookieSyncsProcessed


def getPrimaryEmissionsPerCookieSync(
    serverAllocation: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    serverEmissionsG = (
        getFactOrDefault("server emissions mt per month", facts, defaults, depth - 1)
        * 1000000
    )
    cookieSyncRequests = getCookieSyncsProcessed(facts, defaults, depth - 1)
    serversProcessingCookieSyncs = (
        getFactOrDefault(
            "servers processing cookie syncs pct", facts, defaults, depth - 1
        )
        / 100.0
    )
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    primaryEmissionsPerCookieSync = (
        serverAllocation
        * serverEmissionsG
        * serversProcessingCookieSyncs
        / cookieSyncRequests
    )
    verboseprint(
        f"{'  ' * depth}primary emissions g per cookie sync: {primaryEmissionsPerCookieSync} (calculation)"
    )
    return primaryEmissionsPerCookieSync


def getSecondaryEmissionsPerCookieSync(
    model: AdTechPlatform, distributionPartners: list[DistributionPartner]
) -> float:
    secondaryEmissionsPerCookieSync = 0.0
    for edge in distributionPartners:
        secondaryEmissionsPerCookieSync += edge.partner.primaryCookieSyncEmissions
    secondaryEmissionsPerCookieSync *= model.cookieSyncDistributionRate
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}secondary emissions g per cookie sync: {secondaryEmissionsPerCookieSync:.6f} (calculation using {len(distributionPartners)} partners)"
    )
    return secondaryEmissionsPerCookieSync


depth = 4 if args.verbose else 0
productModels = []
for p in document["company"]["products"]:
    product = p["product"]
    if "name" not in product:
        raise Exception(f"No 'name' field found in a product")

    verboseprint(f"#### {product['name']}")
    template = getProductInfo("template", None, product, 0)
    identifier = getProductInfo("identifier", None, product, 0)
    serverAllocation = getProductInfo("server allocation pct", 100, product, 0) / 100
    corporateAllocation = (
        getProductInfo("corporate allocation pct", 100, product, 0) / 100
    )
    if template not in defaultsDocument["defaults"]:
        raise Exception(f"Template {template} not found in defaults")
    defaults = defaultsDocument["defaults"][template]
    primaryEmissionsPerBidRequest = getPrimaryEmissionsPerBidRequest(
        serverAllocation, corporateAllocation, facts, defaults, depth
    )
    primaryEmissionsPerCookieSync = getPrimaryEmissionsPerCookieSync(
        serverAllocation, facts, defaults, depth
    )
    cookieSyncDistributionRatio = getFactOrDefault(
        "cookie sync distribution ratio", facts, defaults, depth - 1
    )
    bidRequestRejectionRate = (
        getFactOrDefault("bid request rejection pct", facts, defaults, depth - 1)
        / 100.0
    )
    model = AdTechPlatform(
        product["name"],
        identifier,
        primaryEmissionsPerBidRequest,
        primaryEmissionsPerCookieSync,
        cookieSyncDistributionRatio,
        bidRequestRejectionRate,
    )
    productModel = {"product": model}
    productModels.append(productModel)

print(yaml.dump({"products": productModels}, Dumper=yaml.Dumper))

if args.partners and args.verbose:
    distributionPartners: list[DistributionPartner] = []
    for i in range(args.partners):
        partner = AdTechPlatform(f"dummy {i}", f"dummy{i}.com", 0.001, 0.0001, 1.0, 0.3)
        distributionPartners.append(DistributionPartner(partner, 1.0))

    getSecondaryEmissionsPerBidRequest(
        productModels[0]["product"], distributionPartners
    )
    getSecondaryEmissionsPerCookieSync(
        productModels[0]["product"], distributionPartners
    )
