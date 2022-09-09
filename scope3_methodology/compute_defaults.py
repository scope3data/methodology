#!/usr/bin/env python
import argparse
from glob import glob

import yaml
from adtech_model import get_ad_tech_model_keys
from corporate import get_corporate_keys
from utils import get_all_facts
from yaml.loader import SafeLoader


def compute_defaults(
    template_type: str,
    templates: dict[str, dict[str, float]],
    facts: dict[str, float],
    defaults_file: str,
    model_inputs: set[str],
    dry_run: bool,
):
    global_defaults: dict[str, float] = {
        # TODO - get some actual data on this from customers
        "bid request size in bytes": 10000,
    }

    template_defaults = {}

    for name, template in templates.items():
        if str(template["type"]) != template_type:
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
                elif input in global_defaults:
                    defaults[input] = global_defaults[input]

        template_defaults[name] = defaults

    output = yaml.dump({"defaults": template_defaults}, Dumper=yaml.Dumper)
    if dry_run:
        print(output)
    else:
        write_stream = open(defaults_file, "w")
        write_stream.write(output)
        write_stream.close()


def main():
    parser = argparse.ArgumentParser(description="Compute defaults from known sources")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the defaults but don't write to file",
    )
    args = parser.parse_args()

    template_keys = {}
    template_keys["organization"] = get_corporate_keys()
    template_keys["property"] = {
        "quality impressions per duration s",
        "revenue allocation to digital pct",
        "revenue allocation to ads pct",
        "end-user data transfer electricity use kwh per gb",
        "core internet data transfer electricity use kwh per gb",
        "computer active electricity use watts",
        "computer idle electricity use watts",
    }
    template_keys["atp"] = get_ad_tech_model_keys()

    # get a list of all facts from our sources
    facts = get_all_facts()

    templates = {}
    template_files = glob("templates/*.yaml")
    for file in template_files:
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

    for t in template_keys:
        compute_defaults(t, templates, facts, t + "-defaults.yaml", template_keys[t], args.dry_run)


if __name__ == "__main__":
    main()
