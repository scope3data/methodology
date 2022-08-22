from glob import glob
import yaml
from yaml.loader import SafeLoader
from typing import Dict, List
import argparse

parser = argparse.ArgumentParser(description="Compute defaults from known sources")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to use (overrides defaults.yaml)",
)
parser.add_argument(
    "--dry-run", action="store_true", help="Print the defaults but don't write to file"
)
args = parser.parse_args()

# get a list of all facts from our sources
facts: Dict[str, List[float]] = {}

files = glob("sources/**/*.yaml", recursive=True)
for file in files:
    stream = open(file, "r")
    documents = list(yaml.load_all(stream, Loader=SafeLoader))
    for document in documents:
        if "company" not in document:
            print("No company found in " + document)
            continue
        if "sources" not in document["company"]:
            print("No sources found in " + document)
            continue
        for source in document["company"]["sources"]:
            for fact in source["source"]["facts"]:
                keys = [
                    key
                    for key in fact["fact"]
                    if key != "reference" and key != "comment"
                ]
                for key in keys:
                    if key not in facts:
                        facts[key] = []
                    facts[key].append(fact["fact"][key])

relevantDefaults = {
    "travel emissions mt per employee per month",
    "office emissions mt per employee per month",
    "commuting emissions mt per employee per month",
}

defaults: Dict[str, float] = {}
for key in facts:
    if key in relevantDefaults:
        defaults[key] = sum(facts[key]) / len(facts[key])

output = yaml.dump({"defaults": defaults}, Dumper=yaml.Dumper)
if args.dry_run:
    print(output)
else:
    writeStream = open(args.defaultsFile, "w")
    writeStream.write(output)
    writeStream.close()
