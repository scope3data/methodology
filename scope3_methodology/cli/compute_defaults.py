#!/usr/bin/env python
""" Compute defaults for all templates types [atp, property, organization ] """
import argparse
from dataclasses import dataclass
from decimal import Decimal
from glob import glob
from typing import Optional

from scope3_methodology.ad_tech_platform.model import AdTechPlatform
from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.end_user_device.model import EndUserDevice
from scope3_methodology.networking.model import NetworkingConnection
from scope3_methodology.networking.transmission_rate_model import TransmissionRate
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
    channel: Optional[str],
    facts: dict[str, list[Fact]],
    model_inputs: set[str],
):
    """
    Build a view of average across all templates within the model
    (i.e. model: atp templates: ssp, dsp, network) AND build a view specific to the template
    we are looking at (i.e. average of only DSP facts) If a channel is provided, the an average
    of the channel-template view is built (i.e. average of only display channel facts)
    :return: FactAverages
    """
    all_average_defaults: dict[str, Decimal] = {}
    all_average_defaults_source_list: dict[str, list[Fact]] = {}
    template_average_defaults: dict[str, Decimal] = {}
    template_average_defaults_source_list: dict[str, list[Fact]] = {}

    template_key = "{channel}-{template}" if channel else template
    for key in facts:
        all_fact_source_list: list[Fact] = []
        template_specific_source_list: list[Fact] = []
        if key in model_inputs:
            all_fact_sum = Decimal(0)
            template_specific_sum = Decimal(0)
            template_fact_count = 0
            for fact in facts[key]:
                all_fact_source_list.append(fact)
                fact_key = "{fact.channel}-{fact.template}" if fact.channel else fact.template
                if fact_key == template_key:
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


@dataclass
class BuiltDefaults:
    """Build and return default and default source list"""

    defaults: dict[str, Decimal]
    defaults_source_list: dict[str, list[str]]


def build_defaults_and_source_list(
    channel_name: str | None,
    template_name: str,
    facts: dict[str, list[Fact]],
    model_inputs: set[str],
    template_info: dict[str, Decimal],
):
    """Compute defaults for a template type"""
    global_defaults: dict[str, Decimal] = {
        # TODO - get some actual data on this from customers
        "bid_request_size_in_bytes": Decimal("10000.0"),
        "bid_request_distribution_rate": Decimal("1.0"),
    }

    # Determine fact averages
    averages_info = build_fact_averages(template_name, channel_name, facts, model_inputs)

    # Determine which defaults to use and build list of the final source list
    defaults: dict[str, Decimal] = {}
    defaults_source_list: dict[str, list[str]] = {}
    for key_input in model_inputs:
        # First check is we have a template specific average
        if key_input in averages_info.template_average_defaults:
            defaults[key_input] = averages_info.template_average_defaults[key_input]
            defaults_source_list[key_input] = averages_info.template_average_defaults_source_list[
                key_input
            ]
        # Then check if we have a template specific override (from /template/<type>.yaml)
        elif key_input in template_info:
            defaults[key_input] = template_info[key_input]
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

    return BuiltDefaults(defaults=defaults, defaults_source_list=defaults_source_list)


def compute_defaults(
    model: str,
    templates: dict[str, dict[str, Decimal]],
    facts: dict[str, list[Fact]],
    model_defaults_file: str,
    model_inputs: set[str],
    dry_run: bool,
    defaults_directory: str,
):
    """Compute defaults for a template type"""
    template_defaults = {}  # type: ignore
    template_defaults_sources = {}  # type: ignore
    for _, template in templates.items():
        template_name = str(template["name"])
        if str(template["type"]) != model:
            continue
        channel_name = str(template["channel"]) if "channel" in template else None

        # Determine which defaults to use and build list of the final source list
        built_defaults = build_defaults_and_source_list(
            channel_name, template_name, facts, model_inputs, template
        )

        if channel_name:
            if channel_name not in template_defaults:
                template_defaults[channel_name] = {}
                template_defaults_sources[channel_name] = {}

            template_defaults[channel_name][template_name] = built_defaults.defaults
            template_defaults_sources[channel_name][
                template_name
            ] = built_defaults.defaults_source_list
        else:
            template_defaults[template_name] = built_defaults.defaults
            template_defaults_sources[template_name] = built_defaults.defaults_source_list

    output = "# AUTO_GENERATED by scope3_methodology/cli/compute_defaults.py \n"
    output += yaml_dump({"defaults": template_defaults, "sources": template_defaults_sources})
    if dry_run:
        print(output)
    else:
        file_path = f"{defaults_directory}/{model_defaults_file}"
        with open(file_path, "w", encoding="UTF-8") as write_stream:
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
    parser.add_argument(
        "-d",
        "--defaults_directory",
        default="defaults",
        help="Set the defaults file directory to use",
    )
    args = parser.parse_args()

    model_keys = {}
    model_keys["organization"] = CorporateEmissions.default_fields()
    model_keys["property"] = Property.default_fields()
    model_keys["atp"] = AdTechPlatform.default_fields()
    model_keys["end_user_device"] = EndUserDevice.default_fields()
    model_keys["networking"] = NetworkingConnection.default_fields()
    model_keys["transmission_rate"] = TransmissionRate.default_fields()

    # get a list of all facts from our sources
    facts = get_all_facts()

    templates = {}
    template_files = glob("templates/*/*.yaml")
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
            channel = document["template"]["channel"] if "channel" in document["template"] else ""
            template_key = f"{name}-{template_type}-${channel}"
            templates[template_key] = document["template"]

    for model, keys in model_keys.items():
        compute_defaults(
            model,
            templates,
            facts,
            model + "-defaults.yaml",
            keys,
            args.dry_run,
            args.defaults_directory,
        )


if __name__ == "__main__":
    main()
