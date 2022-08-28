#!/usr/bin/env python
import argparse
from glob import glob

import yaml
from yaml.loader import SafeLoader


def main():
    parser = argparse.ArgumentParser(description="Compute defaults from known sources")
    parser.add_argument(
        "-d",
        "--defaultsFile",
        default="defaults.yaml",
        help="Set the defaults file to output to (overrides defaults.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the defaults but don't write to file",
    )
    args = parser.parse_args()

    corporate_model_inputs = {
        "corporate emissions mt per month",
        "travel emissions mt per employee per month",
        "office emissions mt per employee per month",
        "commuting emissions mt per employee per month",
        "it emissions mt per employee per month",
    }

    ad_tech_model_inputs = {
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

    property_model_inputs = {
        "quality impressions per duration s",
        "revenue allocation to digital pct",
        "revenue allocation to ads pct",
    }

    atp_model_inputs = corporate_model_inputs.union(ad_tech_model_inputs)

    globalDefaults: dict[str, float] = {
        # TODO - get some actual data on this from customers
        "bid request size in bytes": 10000,
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
                for fact in source["facts"]:
                    keys = [key for key in fact if key != "reference" and key != "comment"]
                    for key in keys:
                        if key not in facts:
                            facts[key] = []
                        facts[key].append(fact[key])

    templates = {}
    templateFiles = glob("templates/*.yaml")
    for file in templateFiles:
        stream = open(file, "r")
        document = yaml.load(stream, Loader=SafeLoader)
        if "template" not in document:
            raise Exception(f"'template' field not found in {file}")
        if "name" not in document["template"]:
            raise Exception(f"'name' field not found in {file}")
        if "type" not in document["template"]:
            raise Exception(f"'type' field not found in {file}")
        name = document["template"]["name"]
        templates[name] = document["template"]

    templateDefaults = {}

    for name, template in templates.items():
        model_inputs: set[str]
        if template["type"] == "publisher":
            model_inputs = corporate_model_inputs
        elif template["type"] == "property":
            model_inputs = property_model_inputs
        else:
            model_inputs = atp_model_inputs
        defaults: dict[str, float] = {}
        for key in facts:
            if key in model_inputs:
                defaults[key] = round(sum(facts[key]) / len(facts[key]), 4)

        for input in model_inputs:
            if input not in defaults:
                if input in template:
                    defaults[input] = template[input]
                elif input in globalDefaults:
                    defaults[input] = globalDefaults[input]
        templateDefaults[name] = defaults

    output = yaml.dump({"defaults": templateDefaults}, Dumper=yaml.Dumper)
    if args.dry_run:
        print(output)
    else:
        writeStream = open(args.defaultsFile, "w")
        writeStream.write(output)
        writeStream.close()


if __name__ == "__main__":
    main()
