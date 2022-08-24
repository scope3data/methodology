import yaml
from yaml.loader import SafeLoader
from typing import Dict, List
import argparse

# TODO - support templates/variants so we load different defaults by atp type

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
    corporateEmissionsG = getCorporateEmissions(facts, defaults, depth - 1) * 1000000
    bidRequests = (
        getFactOrDefault("bid requests processed billion per month", facts, defaults, depth - 1) * 1000000000
    )
    corporateEmissionsPerBidRequest = corporateEmissionsG / bidRequests
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    verboseprint(
        f"{'  ' * depth}corporate emissions g per bid request: {corporateEmissionsPerBidRequest:.8f} (calculation)"
    )
    return corporateEmissionsPerBidRequest


def getExternalRequestRatio(facts: Dict[str, float], defaults: Dict[str, float], depth: int) -> float:
    if (
        "ad tech platform bid requests processed billion per month" in facts
        and "bid requests processed billion per month" in facts
    ):
        atpRequests = getFactOrDefault(
            "ad tech platform bid requests processed billion per month", facts, defaults, depth - 1
        )
        bidRequests = getFactOrDefault(
            "bid requests processed billion per month", facts, defaults, depth - 1
        )
        ratio = atpRequests / bidRequests
        verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
        verboseprint(f"{'  ' * depth}external request ratio: {ratio * 100.0:.1f}% (calculation)")
        return ratio
    return getFactOrDefault("pct of bid requests processed from ad tech platforms", facts, defaults, depth) / 100


def getDataTransferEmissionsPerBidRequest(
    facts: Dict[str, float], defaults: Dict[str, float], depth: int
) -> float:
    if "data transfer emissions mt per month" in facts:
        return getFactOrDefault("data transfer emissions mt per month", facts, defaults, depth)

    externalRequestRatio = getExternalRequestRatio(facts, defaults, depth - 1)
    bidRequestSizeGB = (
        getFactOrDefault("bid request size in bytes", facts, defaults, depth - 1) / 1024 / 1024 / 1024
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


def getServerEmissions(
    facts: Dict[str, float], defaults: Dict[str, float], depth: int
) -> float:
    if "server emissions mt per month" in facts:
        return getFactOrDefault("server emissions mt per month", facts, defaults, depth)

def getServerEmissionsPerBidRequest(
    facts: Dict[str, float], defaults: Dict[str, float], depth: int
) -> float:
    serverEmissionsG = getFactOrDefault("server emissions mt per month", facts, defaults, depth - 1) * 1000000
    bidRequests = getFactOrDefault(
        "bid requests processed billion per month", facts, defaults, depth - 1
    ) * 1000000000
    serversProcessingBidRequests = getFactOrDefault("servers processing bid requests pct", facts, defaults, depth - 1) / 100.0
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    serverEmissionsPerBidRequest = serverEmissionsG * serversProcessingBidRequests / bidRequests
    verboseprint(
        f"{'  ' * depth}server emissions g per bid request: {serverEmissionsPerBidRequest:.6f} (calculation)")
    return serverEmissionsPerBidRequest

def getPrimaryEmissionsPerBidRequest(
    facts: Dict[str, float], defaults: Dict[str, float], depth: int
) -> float:
    corporateEmissionsPerBidRequest = getCorporateEmissionsPerBidRequest(facts, defaults, depth - 1)
    dataTransferEmissionsPerBidRequest = getDataTransferEmissionsPerBidRequest(facts, defaults, depth - 1)
    serverEmissionsPerBidRequest = getServerEmissionsPerBidRequest(facts, defaults, depth - 1)
    verboseprint(f"{'  ' * (depth - 1)}-------------------------------------------")
    primaryEmissionsPerBidRequest = corporateEmissionsPerBidRequest + dataTransferEmissionsPerBidRequest + serverEmissionsPerBidRequest
    verboseprint(
        f"{'  ' * depth}primary emissions mt per billion bid requests: {primaryEmissionsPerBidRequest:.6f} (calculation)"
    )
    return primaryEmissionsPerBidRequest


depth = 4 if args.verbose else 0

modelInput = {
    "primaryEmissionsGPerBidRequest": round(getPrimaryEmissionsPerBidRequest(facts, defaults, depth), 8)
}

print(yaml.dump({"ATPModelInput": modelInput}, Dumper=yaml.Dumper))
