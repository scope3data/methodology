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
parser.add_argument("-v", "--verbose", action="store_true", help="Show derivation of output")
parser.add_argument("companyFile", nargs=1, help="The company file to parse in YAML format")
args = parser.parse_args()

if args.verbose:

    def verboseprint(*args, **kwargs):
        print(*args, **kwargs)

else:
    verboseprint = lambda *a, **k: None  # do-nothing function

# Load defaults
defaultsStream = open(args.defaultsFile, "r")
defaultsDocument = yaml.load(defaultsStream, Loader=SafeLoader)
defaults = defaultsDocument["defaults"]

# Load facts about the company
facts: Dict[str, float] = {}
stream = open(args.companyFile[0], "r")
documents = list(yaml.load_all(stream, Loader=SafeLoader))
for document in documents:
    if "company" not in document:
        raise Exception("No company found in " + document)
    if "sources" not in document["company"]:
        raise Exception("No sources found in " + document)
        continue
    for source in document["company"]["sources"]:
        for fact in source["source"]["facts"]:
            keys = [key for key in fact["fact"] if key != "reference" and key != "comment"]
            for key in keys:
                facts[key] = fact["fact"][key]


def getFactOrDefault(key: str, facts: Dict[str, float], defaults: Dict[str, float], depth: int) -> float:
    if key in facts:
        verboseprint(f"{'  ' * depth}{key} = {facts[key]}")
        return facts[key]
    if key in defaults:
        verboseprint(f"{'  ' * depth}{key} = {defaults[key]} (default)")
        return defaults[key]
    raise Exception(f"No default found for '{key}'")


def getCorporateEmissions(facts: Dict[str, float], defaults: Dict[str, float], depth: int) -> float:
    if "corporate emissions mt per month" in facts:
        return getFactOrDefault("corporate emissions mt per month", facts, defaults, depth)
    if not "employees" in facts:
        raise Exception("Must provide either 'corporate emissions mt per month' or 'employees'")
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
    verboseprint(f"{'  ' * depth}corporate emissions mt per month: {corporateEmissions:.2f} (calculation)")
    return corporateEmissions


def getCorporateEmissionsPerBidRequest(
    facts: Dict[str, float], defaults: Dict[str, float], depth: int
) -> float:
    corporateEmissionsMT = getCorporateEmissions(facts, defaults, depth - 1)
    bidRequests = getFactOrDefault("bid requests processed billion per month", facts, defaults, depth - 1)
    corporateEmissionsPerBidRequest = corporateEmissionsMT / bidRequests
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}corporate emissions mt per billion bid requests: {corporateEmissionsPerBidRequest:.4f} (calculation)"
    )
    return corporateEmissionsPerBidRequest


depth = 3 if args.verbose else 0
corporateEmissionsPerBidRequest = getCorporateEmissionsPerBidRequest(facts, defaults, depth - 1)
verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
print(f"{'  ' * depth}corporate emissions g per bid request: {corporateEmissionsPerBidRequest/1000:.6f}")
