""" Util functions used across modules """

import logging
from decimal import Decimal
from glob import glob
from pathlib import Path
from typing import Optional

from scope3_methodology.utils.yaml_helpers import yaml_load


class Fact:
    """A fact from one of our sources"""

    def __init__(
        self,
        company: str,
        url: str | None,
        is_calculation: bool,
        value: Decimal,
        template: str,
        channel: str | None,
        key: str,
    ) -> None:
        self.company = company
        self.url = "n/a" if not url else url
        self.is_calculation = is_calculation
        self.value = value
        self.template = template
        self.channel = channel
        self.key = key

    def __repr__(self):
        calc = " (calculation)" if self.is_calculation else ""
        if self.channel:
            return f"{self.company}({self.channel}{self.template}){calc} {self.key}: {self.value}"
        return f"{self.company}({self.template}){calc} {self.key}: {self.value}"


def not_none(value: Optional[Decimal]) -> Decimal:
    """Verifies the value is not none or raises an exception"""
    if value is not None:
        return value
    raise Exception("Attempting operation with None value")


def log_step(key: str, value: str | Decimal | None, source: str, depth: int) -> None:
    """Takes in a ke, value, and depth and logs the step"""
    logging.info("%s%s = %s (%s)", "  " * depth, key, value, source)


def log_result(key: str, value: str | Decimal | None, depth: int) -> None:
    """Takes in a ke, value, and depth and logs the result"""
    logging.info("%s -------------------------------------------", ("  " * (depth - 1)))
    logging.info("%s %s = %s (calculation)", ("  " * depth), key, value)


def get_facts(facts: list[dict[str, Decimal]]) -> dict[str, Decimal | str]:
    """Extract all raw facts from list of facts dictionaries extracted"""
    raw_facts: dict[str, Decimal | str] = {}
    for fact in facts:
        keys = [
            key for key in fact if key not in ["reference", "comment", "source_id", "calculation"]
        ]
        for key in keys:
            raw_facts[key] = fact[key]
    return raw_facts


def populate_facts(
    facts: dict[str, list[Fact]], company: str, template: str, channel: str | None, sources
) -> None:
    """Extract all raw facts from sources and adds to all facts dictionary"""
    for source in sources:
        is_calculation = "calculation" in source
        url = source["url"] if "url" in source else ""
        if "facts" not in source:
            continue
        for fact in source["facts"]:
            keys = [key for key in fact if key not in ["reference", "comment", "source_id"]]
            for key in keys:
                if key not in facts:
                    facts[key] = []
                facts[key].append(
                    Fact(company, url, is_calculation, fact[key], template, channel, key)
                )


def populate_raw_facts(
    all_facts: dict[str, list[Fact]],
    company: str,
    template: str,
    channel: str | None,
    facts: dict[str, Decimal],
) -> None:
    """Extract all raw facts from list of facts dictionaries and adds to all facts dictionary"""
    for fact in facts:
        keys = [key for key in fact if key not in ["reference", "comment", "source_id"]]
        for key in keys:
            if key not in all_facts:
                all_facts[key] = []
            all_facts[key].append(
                Fact(
                    company=company,
                    url="",
                    is_calculation="calculation" in fact,
                    value=fact[key],  # type: ignore
                    template=template,
                    channel=channel,
                    key=key,
                )
            )


GENERAL_FACT = "GENERAL"


def get_all_facts() -> dict[str, list[Fact]]:
    """Extract all facts from all yaml files under data"""
    facts: dict[str, list[Fact]] = {}
    files = glob("data/**/*.yaml", recursive=True)
    for file in files:
        with open(file, "r", encoding="UTF-8") as stream:
            document = yaml_load(stream)
            pth = Path(file)
            if "company" in document and "sources" in document["company"]:
                template = (
                    document["company"]["template"]
                    if "template" in document["company"]
                    else GENERAL_FACT
                )
                channel = (
                    document["company"]["channel"] if "channel" in document["company"] else None
                )
                populate_facts(
                    facts,
                    "/".join(pth.parts[-2:]),
                    template,
                    channel,
                    document["company"]["sources"],
                )
            if "sources" in document:
                template = document["template"] if "template" in document else GENERAL_FACT
                channel = document["channel"] if "channel" in document else None
                populate_facts(
                    facts, "/".join(pth.parts[-2:]), template, channel, document["sources"]
                )
            if "facts" in document:
                template = document["template"] if "template" in document else GENERAL_FACT
                channel = document["channel"] if "channel" in document else None
                populate_raw_facts(
                    facts, "/".join(pth.parts[-2:]), template, channel, document["facts"]
                )
            if "products" in document:
                for product in document["products"]:
                    if "facts" in product:
                        populate_raw_facts(
                            facts,
                            "/".join(pth.parts[-2:]),
                            product["template"],
                            None,
                            product["facts"],
                        )
            if "properties" in document:
                for publisher_property in document["properties"]:
                    populate_raw_facts(
                        facts,
                        "/".join(pth.parts[-2:]),
                        publisher_property["template"],
                        publisher_property["channel"],
                        publisher_property["facts"],
                    )
    return facts
