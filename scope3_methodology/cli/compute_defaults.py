#!/usr/bin/env python
""" Compute defaults for all templates types [atp, property, organization ] """
import argparse
from dataclasses import dataclass
from decimal import Decimal
from glob import glob

from scope3_methodology.ad_tech_platform.model import AdTechPlatform
from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.publisher.model import Property
from scope3_methodology.utils.utils import Fact, get_all_facts
from scope3_methodology.utils.yaml_helpers import yaml_dump, yaml_load


@dataclass
class FactAverages:
    """Fact averages returned by build_fact_averages"""

    all_average_defaults: dict[str, Decimal]
    all_average_defaults_source_list: dict[str, list[Fact]]
    template_average_defaults: dict[str, Decimal]
    template_average_defaults_source_list: dict[str, list[Fact]]


def build_fact_averages(
    template: str,
    facts: dict[str, list[Fact]],
    model_inputs: set[str],
):
    """
    Build a view of average across all templates within the model
    (i.e. model: atp templates: ssp, dsp, network) AND build a view specific to the template
    we are looking at (i.e. average of only DSP facts)
    :return: FactAverages
    """
    all_average_defaults: dict[str, Decimal] = {}
    all_average_defaults_source_list: dict[str, list[Fact]] = {}
    template_average_defaults: dict[str, Decimal] = {}
    template_average_defaults_source_list: dict[str, list[Fact]] = {}

    for key in facts:
        all_fact_source_list: list[Fact] = []
        template_specific_source_list: list[Fact] = []
        if key in model_inputs:
            all_fact_sum = Decimal(0)
            template_specific_sum = Decimal(0)
            template_fact_count = 0
            for fact in facts[key]:
                all_fact_source_list.append(fact)
                if fact.template == template:
                    template_specific_source_list.append(fact)
                    template_specific_sum += fact.value
                    template_fact_count += 1
                all_fact_sum += fact.value

            all_average_defaults[key] = all_fact_sum / Decimal(len(facts[key]))
            all_average_defaults_source_list[key] = all_fact_source_list
            if template_fact_count > 0:
                template_average_defaults[key] = template_specific_sum / Decimal(
                    template_fact_count
                )
                template_average_defaults_source_list[key] = template_specific_source_list

    return FactAverages(
        all_average_defaults=all_average_defaults,
        all_average_defaults_source_list=all_average_defaults_source_list,
        template_average_defaults=template_average_defaults,
        template_average_defaults_source_list=template_average_defaults_source_list,
    )


def compute_defaults(
    model: str,
    templates: dict[str, dict[str, Decimal]],
    facts: dict[str, list[Fact]],
    model_defaults_file: str,
    model_inputs: set[str],
    dry_run: bool,
):
    """Compute defaults for a template type"""
    global_defaults: dict[str, Decimal] = {
        # TODO - get some actual data on this from customers
        "bid_request_size_in_bytes": Decimal("10000.0"),
        "bid_request_distribution_rate": Decimal("1.0"),
    }

    template_defaults = {}
    template_defaults_sources = {}

    for _, template in templates.items():
        name = template["name"]
        if str(template["type"]) != model:
            continue

        # Determine fact averages
        averages_info = build_fact_averages(str(template["template"]), facts, model_inputs)

        # Determine which defaults to use and build list of the final source list
        defaults: dict[str, Decimal] = {}
        defaults_source_list: dict[str, list[str]] = {}
        for key_input in model_inputs:
            # First check is we have a template specific average
            if key_input in averages_info.template_average_defaults:
                defaults[key_input] = averages_info.template_average_defaults[key_input]
                defaults_source_list[
                    key_input
                ] = averages_info.template_average_defaults_source_list[key_input]
            # Then check if we have a template specific override (from /template/<type>.yaml)
            elif key_input in template:
                defaults[key_input] = template[key_input]
                defaults_source_list[key_input] = ["template default"]
            # Then check if there is an average across all the model templates
            elif key_input in averages_info.all_average_defaults:
                defaults[key_input] = averages_info.all_average_defaults[key_input]
                defaults_source_list[key_input] = averages_info.all_average_defaults_source_list[
                    key_input
                ]
            # Then check global defaults
            elif key_input in global_defaults:
                defaults[key_input] = global_defaults[key_input]
                defaults_source_list[key_input] = ["global default"]

        template_defaults[name] = defaults
        template_defaults_sources[name] = defaults_source_list

    output = yaml_dump({"defaults": template_defaults, "sources": template_defaults_sources})
    if dry_run:
        print(output)
    else:
        with open(model_defaults_file, "w", encoding="UTF-8") as write_stream:
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

    model_keys = {}
    model_keys["organization"] = CorporateEmissions.default_fields()
    model_keys["property"] = Property.default_fields()
    model_keys["atp"] = AdTechPlatform.default_fields()

    # get a list of all facts from our sources
    facts = get_all_facts()

    templates = {}
    template_files = glob("templates/*.yaml")
    for file in template_files:
        with open(file, "r", encoding="UTF-8") as stream:
            document = yaml_load(stream)
            if "template" not in document:
                raise Exception(f"'template' field not found in {file}")
            if "name" not in document["template"]:
                raise Exception(f"'name' field not found in {file}")
            if "type" not in document["template"]:
                raise Exception(f"'type' field not found in {file}")
            name = document["template"]["name"]
            template_type = document["template"]["type"]
            template_key = f"{name}-{template_type}"
            templates[template_key] = document["template"]

    for model, keys in model_keys.items():
        compute_defaults(
            model,
            templates,
            facts,
            model + "-defaults.yaml",
            keys,
            args.dry_run,
        )


if __name__ == "__main__":
    main()
