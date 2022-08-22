import yaml
from yaml.loader import SafeLoader
from typing import Dict, List
import argparse

# Parse command line to get company file
parser = argparse.ArgumentParser(description="Compute emissions for an ad tech company")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to use (overrides defaults.yaml)",
)
parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
args = parser.parse_args()

# Load defaults
defaultsStream = open(args.defaultsFile, "r")
defaultsDocument = yaml.load(defaultsStream, Loader=SafeLoader)
defaults = defaultsDocument['defaults']

# Load facts about the company
facts: Dict[str, float] = {}
stream = open(args.companyFile[0], "r")
documents = list(yaml.load_all(stream, Loader=SafeLoader))
for document in documents:
    print(document)
    if "company" not in document:
        print("No company found in " + document)
        continue
    if "sources" not in document["company"]:
        print("No sources found in " + document)
        continue
    for source in document["company"]["sources"]:
        for fact in source["source"]["facts"]:
            keys = [key for key in fact["fact"] if key != "reference" and key != "comment"]
            for key in keys:
                facts[key] = fact["fact"][key]
print(facts)


def getFactOrDefault(key: str, facts: Dict[str, float], defaults: Dict[str, float]) -> float:
    if key in facts:
        return facts[key]
    if key in defaults:
        return defaults[key]
    raise Exception(f"No default found for '{key}'")


def getCorporateEmissions(facts: Dict[str, float], defaults: Dict[str, float]) -> float:
    if "corporate emissions mt per month" in facts:
        return getFactOrDefault("corporate emissions mt per month", facts, defaults)
    if not "employees" in facts:
        raise Exception("Must provide either 'corporate emissions mt per month' or 'employees'")
    officeEmissionsPerEmployee = getFactOrDefault("office emissions mt per employee per month", facts, defaults)
    travelEmissionsPerEmployee = getFactOrDefault("travel emissions mt per employee per month", facts, defaults)
    commutingEmissionsPerEmployee = getFactOrDefault("commuting emissions mt per employee per month", facts, defaults)
    otherEmissionsPerEmployee = getFactOrDefault("other emissions mt per employee per month", facts, defaults)
    return facts["employees"] * (
        officeEmissionsPerEmployee
        + travelEmissionsPerEmployee
        + commutingEmissionsPerEmployee
        + otherEmissionsPerEmployee
    )


def getCorporateEmissionsPerBidRequest(facts: Dict[str, float], defaults: Dict[str, float]) -> float:
    corporateEmissionsMT = getCorporateEmissions(facts, defaults)
    bidRequestWeighting = getFactOrDefault("bid request emissions allocation pct", facts, defaults)
    bidRequests = getFactOrDefault("bid requests billion per month", facts, defaults)


corporateEmissionsPerBidRequest = getCorporateEmissionsPerBidRequest(facts, defaults)
print(f"Corporate Emissions per bid request: %(corporateEmissionsPerBidRequest)")
