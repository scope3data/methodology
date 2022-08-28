#!/usr/bin/env python
import argparse
import logging

import yaml
from corporate import get_corporate_emissions
from utils import get_fact_or_default, get_facts_from_sources, log_result
from yaml.loader import SafeLoader

# Parse command line to get company file
parser = argparse.ArgumentParser(description="Compute emissions for an publisher")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to use (overrides defaults.yaml)",
)
parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
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
if "properties" not in document["company"]:
    raise Exception("No 'properties' field found in company file")
if "sources" not in document["company"]:
    raise Exception("No 'sources' field found in company file")
facts: dict[str, float] = get_facts_from_sources(document["company"]["sources"])

if "publisher" not in defaultsDocument["defaults"]:
    raise Exception("Publisher template not found")
corporate_emissions = (
    get_corporate_emissions(facts, defaultsDocument["defaults"]["publisher"], 0) * 1000000
)

depth = 4 if args.verbose else 0


class Property:
    def __init__(
        self,
        identifier: str,
        impressions: int,
        ad_revenue_allocation: float,
    ) -> None:
        self.identifier = identifier
        self.impressions = impressions
        self.ad_revenue_allocation = ad_revenue_allocation

    def set_corporate_emissions(self, emissions: float) -> None:
        self.corporate_emissions_per_impression = round(
            emissions * self.ad_revenue_allocation / self.impressions, 6
        )
        log_result(
            f"{self.identifier} corporate emissions g",
            self.corporate_emissions_per_impression,
            1,
        )


publisher_impressions = 0.0
properties: list[Property] = []
for property in document["company"]["properties"]:
    if "identifier" not in property or "template" not in property:
        raise Exception("Each property must have an identifier and a template")
    identifier = get_fact_or_default("identifier", property, None, 1)
    template = get_fact_or_default("template", property, None, 1)
    if template not in defaultsDocument["defaults"]:
        raise Exception(f"Template {template} not found in defaults")
    defaults = defaultsDocument["defaults"][template]

    property_facts = get_facts_from_sources(property["sources"])
    # no defaults for these - they must be provided
    visits = get_fact_or_default("visits per month", property_facts, None, 1)
    average_visit_duration = get_fact_or_default(
        "average visit duration s", property_facts, None, 1
    )
    ad_load = get_fact_or_default("quality impressions per duration s", property_facts, defaults, 1)
    impressions = visits * average_visit_duration * ad_load
    log_result("impressions per month", impressions, 2)
    publisher_impressions += impressions

    digital_revenue_pct = (
        get_fact_or_default("revenue allocation to digital pct", property_facts, defaults, 1) / 100
    )
    ad_revenue_pct = (
        get_fact_or_default("revenue allocation to ads pct", property_facts, defaults, 1) / 100
    )
    ad_revenue_allocation = digital_revenue_pct * ad_revenue_pct
    log_result("ad_revenue_allocation", ad_revenue_allocation, 2)

    properties.append(Property(identifier, impressions, ad_revenue_allocation))

for property in properties:
    property.set_corporate_emissions(
        corporate_emissions * property.impressions / publisher_impressions
    )

"""
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
    cookieSyncDistributionRatio = get_fact_or_default(
        "cookie sync distribution ratio", facts, defaults, depth - 1
    )
    bidRequestRejectionRate = (
        get_fact_or_default("bid request rejection pct", facts, defaults, depth - 1)
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
"""

print(yaml.dump({"properties": properties}, Dumper=yaml.Dumper))
