#!/usr/bin/env python
""" Compute defaults for all templates types [atp, property, organization ] """
import argparse
from glob import glob

import yaml
from ad_tech_platform.model import AdTechPlatform
from corporate.model import CorporateEmissions
from publisher.model import Property
from utils.utils import get_all_facts


def compute_defaults(
    template_type: str,
    templates: dict[str, dict[str, float]],
    facts: dict[str, float],
    defaults_file: str,
    model_inputs: set[str],
    dry_run: bool,
):
    """Compute defaults for a template type"""
    global_defaults: dict[str, float] = {
        # TODO - get some actual data on this from customers
        "bid_request_size_in_bytes": 10000,
    }

    template_defaults = {}

    for name, template in templates.items():
        if str(template["type"]) != template_type:
            continue
        defaults: dict[str, float] = {}
        for key in facts:
            if key in model_inputs:
                fact_sum = sum(fact.value for fact in facts[key])  # type: ignore
                defaults[key] = fact_sum / len(facts[key])  # type: ignore

        for key_input in model_inputs:
            if key_input not in defaults:
                if key_input in template:
                    defaults[key_input] = template[key_input]
                elif key_input in global_defaults:
                    defaults[key_input] = global_defaults[key_input]

        template_defaults[name] = defaults

    output = yaml.dump({"defaults": template_defaults}, Dumper=yaml.Dumper)
    if dry_run:
        print(output)
    else:
        with open(defaults_file, "w") as write_stream:
            write_stream.write(output)
            write_stream.close()


def main():
    """Compute defaults for all template types"""
    parser = argparse.ArgumentParser(description="Compute defaults from known sources")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the defaults but don't write to file",
    )
    args = parser.parse_args()

    template_keys = {}
    template_keys["organization"] = CorporateEmissions.default_fields()
    template_keys["property"] = Property.default_fields()
    template_keys["atp"] = AdTechPlatform.default_fields()

    # get a list of all facts from our sources
    facts = get_all_facts()

    templates = {}
    template_files = glob("templates/*.yaml")
    for file in template_files:
        with open(file, "r") as stream:
            document = yaml.safe_load(stream)
            if "template" not in document:
                raise Exception(f"'template' field not found in {file}")
            if "name" not in document["template"]:
                raise Exception(f"'name' field not found in {file}")
            if "type" not in document["template"]:
                raise Exception(f"'type' field not found in {file}")
            name = document["template"]["name"]
            templates[name] = document["template"]

    for template in template_keys:
        compute_defaults(
            template,
            templates,
            facts,
            template + "-defaults.yaml",
            template_keys[template],
            args.dry_run,
        )


if __name__ == "__main__":
    main()
