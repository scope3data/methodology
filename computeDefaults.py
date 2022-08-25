from glob import glob
import yaml
from yaml.loader import SafeLoader
import argparse

Template = dict[str, float]

parser = argparse.ArgumentParser(description="Compute defaults from known sources")
parser.add_argument(
    "-d",
    "--defaultsFile",
    default="defaults.yaml",
    help="Set the defaults file to output to (overrides defaults.yaml)",
)
parser.add_argument("--dry-run", action="store_true", help="Print the defaults but don't write to file")
args = parser.parse_args()

modelInputs = {
    "travel emissions mt per employee per month",
    "office emissions mt per employee per month",
    "commuting emissions mt per employee per month",
    "it emissions mt per employee per month",
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
    "servers processing bid requests pct",
    "servers processing cookie syncs pct",
    "servers processing creative serving pct",
}

globalDefaults: dict[str, float] = {
    # TODO - get some actual data on this from customers
    "bid request size in bytes": 10000,
    # not used (overridden by template)
    "cookie syncs processed billion per month": 0,
}

# get a list of all facts from our sources
facts: dict[str, list[float]] = {}
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
                keys = [key for key in fact["fact"] if key != "reference" and key != "comment"]
                for key in keys:
                    if key not in facts:
                        facts[key] = []
                    facts[key].append(fact["fact"][key])

templates: dict[str, Template] = {}
templateFiles = glob("templates/*.yaml")
for file in templateFiles:
    stream = open(file, "r")
    document = yaml.load(stream, Loader=SafeLoader)
    if "template" not in document:
        raise Exception(f"'template' field not found in {file}")
    if "name" not in document["template"]:
        raise Exception(f"'name' field not found in {file}")
    name = document["template"]["name"]
    templates[name] = document["template"]

templateDefaults = {}

for name, template in templates.items():
    defaults: dict[str, float] = {}
    for key in facts:
        if key in modelInputs:
            defaults[key] = round(sum(facts[key]) / len(facts[key]), 4)

    for input in modelInputs:
        if input not in defaults:
            if input in template:
                defaults[input] = template[input]
            else:
                defaults[input] = globalDefaults[input]
    templateDefaults[name] = defaults

output = yaml.dump({"defaults": templateDefaults}, Dumper=yaml.Dumper)
if args.dry_run:
    print(output)
else:
    writeStream = open(args.defaultsFile, "w")
    writeStream.write(output)
    writeStream.close()
