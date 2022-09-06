#!/usr/bin/env python
""" Model the emissions for a publisher """
import argparse
import logging

import yaml
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
    "--grid-intensity",
    const=1,
    default=539,
    type=int,
    nargs="?",
    help="Carbon intensity of the energy grid in g per KWh",
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
parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
parser.add_argument(
    "-c",
    "--corporateEmissionsG",
    default=0,
    type=float,
    nargs="?",
    help="Provide the corporate emissions for organization in grams",
)
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
corporate_emissionsG = args.corporateEmissionsG

depth = 4 if args.verbose else 0


class Property:
    """A media property, representing a web site, mobile app, ctv channel, etc"""

    def __init__(
        self,
        identifier: str,
        impressions: int,
        ad_revenue_allocation: float,
        data_transfer_electricity_kwh: float,
        page_load_electricity_kwh: float,
        client_device_emissions_g: float,
    ) -> None:
        self.identifier = identifier
        self.impressions = impressions
        self.ad_revenue_allocation = ad_revenue_allocation
        self.data_transfer_electricity_kwh = data_transfer_electricity_kwh
        self.page_load_electricity_kwh = page_load_electricity_kwh
        self.client_device_emissions_g = client_device_emissions_g

    def set_corporate_emissions(self, emissions: float) -> None:
        self.corporate_emissions_per_impression = round(
            emissions * self.ad_revenue_allocation / self.impressions, 6
        )
        log_result(
            f"{self.identifier} corporate emissions g",
            self.corporate_emissions_per_impression,
            1,
        )


def get_energy_from_page_load(
    device: str,
    active_load_s: float,
    browse_s: float,
    facts: dict[str, float],
    defaults: dict[str, float],
    depth: int,
) -> float:
    active_key = f"{device} active electricity use watts"
    idle_key = f"{device} idle electricity use watts"
    active_watts = get_fact_or_default(active_key, facts, defaults, depth - 1)
    idle_watts = get_fact_or_default(idle_key, facts, defaults, depth - 1)

    total_energy_wh = (active_load_s * active_watts + browse_s * idle_watts) / 3600
    log_result("page load electricity wh", total_energy_wh, depth)

    # TODO - add embodied emissions factor here
    # https://circularcomputing.com/news/carbon-footprint-laptop/
    # https://pics.uvic.ca/sites/default/files/uploads/publications/Teehan,%20P.%20Article,%202013%20%202.pdf
    return total_energy_wh


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
    ads_per_visit = average_visit_duration * ad_load
    log_result("ads per visit", ads_per_visit, 2)
    impressions = visits * ads_per_visit
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

    pages_per_visit = get_fact_or_default("pages per visit", property_facts, defaults, 1)
    load_time = get_fact_or_default("load time s", property_facts, defaults, 1)
    active_page_load_time = pages_per_visit * load_time
    log_result("active page load time", active_page_load_time, depth)
    browse_time = average_visit_duration - active_page_load_time
    log_result("browse time", browse_time, depth)

    # CLIENT DEVICE EMISSIONS
    page_load_energy_per_session = get_energy_from_page_load(
        args.environment, active_page_load_time, browse_time, facts, defaults, depth - 1
    )
    page_load_electricity_kwh = page_load_energy_per_session / 1000 / ads_per_visit
    log_result("page_load_electricity_kwh", page_load_electricity_kwh, 2)

    page_size_mb = get_fact_or_default("page size mb", property_facts, defaults, 1)
    data_transfer_per_impression = page_size_mb / ads_per_visit
    electricity_per_mb = (
        get_fact_or_default(
            "end-user data transfer electricity use kwh per gb", property_facts, defaults, 1
        )
        / 1024
    )
    electricity_per_mb += (
        get_fact_or_default(
            "core internet data transfer electricity use kwh per gb", property_facts, defaults, 1
        )
        / 1024
    )
    data_transfer_electricity_kwh = data_transfer_per_impression * electricity_per_mb
    log_result("data_transfer_electricity_kwh", data_transfer_electricity_kwh, 2)

    client_device_emissions_per_impression = args.grid_intensity * (
        data_transfer_electricity_kwh + page_load_electricity_kwh
    )
    log_result("client_device_emissions", client_device_emissions_per_impression, 2)

    # TODO - simulate auctions to multiple ad tech partners w/ cookie syncs

    properties.append(
        Property(
            identifier,
            impressions,
            ad_revenue_allocation,
            data_transfer_electricity_kwh,
            page_load_electricity_kwh,
            client_device_emissions_per_impression,
        )
    )

for property in properties:
    property.set_corporate_emissions(
        corporate_emissionsG * property.impressions / publisher_impressions
    )

print(yaml.dump({"properties": properties}, Dumper=yaml.Dumper))
