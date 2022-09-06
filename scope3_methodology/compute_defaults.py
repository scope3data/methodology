#!/usr/bin/env python
import argparse
from glob import glob

import yaml
from adtech_model import get_ad_tech_model_keys
from corporate import get_corporate_keys
from utils import get_all_facts
from yaml.loader import SafeLoader


def computeDefaults(
    templateType: str,
    templates: dict[str, dict[str, float]],
    facts: dict[str, float],
    defaultsFile: str,
    model_inputs: set[str],
    dry_run: bool,
):
    globalDefaults: dict[str, float] = {
        # TODO - get some actual data on this from customers
        "bid request size in bytes": 10000,
    }

    templateDefaults = {}

    for name, template in templates.items():
        if str(template["type"]) != templateType:
            continue
        defaults: dict[str, float] = {}
        for key in facts:
            if key in model_inputs:
                fact_sum = sum(fact.value for fact in facts[key])  # type: ignore
                defaults[key] = round(fact_sum / len(facts[key]), 4)  # type: ignore

        for input in model_inputs:
            if input not in defaults:
                if input in template:
                    defaults[input] = template[input]
                elif input in globalDefaults:
                    defaults[input] = globalDefaults[input]

        templateDefaults[name] = defaults

    output = yaml.dump({"defaults": templateDefaults}, Dumper=yaml.Dumper)
    if dry_run:
        print(output)
    else:
        writeStream = open(defaultsFile, "w")
        writeStream.write(output)
        writeStream.close()


def main():
    parser = argparse.ArgumentParser(description="Compute defaults from known sources")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the defaults but don't write to file",
    )
    args = parser.parse_args()

    templateKeys = {}
    templateKeys["organization"] = get_corporate_keys()
    templateKeys["property"] = {
        "quality impressions per duration s",
        "revenue allocation to digital pct",
        "revenue allocation to ads pct",
        "end-user data transfer electricity use kwh per gb",
        "core internet data transfer electricity use kwh per gb",
        "computer active electricity use watts",
        "computer idle electricity use watts",
    }
    templateKeys["atp"] = get_ad_tech_model_keys()

    # get a list of all facts from our sources
    facts = get_all_facts()

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

    for t in templateKeys:
        computeDefaults(t, templates, facts, t + "-defaults.yaml", templateKeys[t], args.dry_run)


if __name__ == "__main__":
    main()
