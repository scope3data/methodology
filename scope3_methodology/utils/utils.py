""" Util functions used across modules """

import logging
from glob import glob
from pathlib import Path
from typing import Optional

import yaml


class Fact:
    """A fact from one of our sources"""

    def __init__(self, company: str, url: str | None, is_calculation: bool, value: float) -> None:
        self.company = company
        self.url = "n/a" if not url else url
        self.is_calculation = is_calculation
        self.value = value

    def __repr__(self):
        return f"{self.company}{' (calculation)' if self.is_calculation else ''}: {self.value}"


def not_none(value: Optional[float]) -> float:
    """Verifies the value is not none or raises an exception"""
    if value is not None:
        return value
    raise Exception("Attempting operation with None value")


def log_step(key: str, value: str, source: str, depth: int) -> None:
    """Takes in a ke, value, and depth and logs the step"""
    logging.info(f"{'  ' * depth}{key} = {value} ({source})")


def log_result(key: str, value: str, depth: int) -> None:
    """Takes in a ke, value, and depth and logs the result"""
    logging.info(f"{'  ' * (depth - 1)}-------------------------------------------")
    logging.info(f"{'  ' * depth}{key} = {value} (calculation)")


def get_facts(facts: list[dict[str, float]]) -> dict[str, float]:
    """Extract all raw facts from list of facts dictionaries extracted"""
    raw_facts: dict[str, float] = {}
    for fact in facts:
        keys = [key for key in fact if key not in ["reference", "comment", "source_id"]]
        for key in keys:
            raw_facts[key] = fact[key]
    return raw_facts


def populate_facts(facts: dict[str, list[Fact]], company: str, sources) -> None:
    """Extract all raw facts from sources and adds to all facts dictionary"""
    for source in sources:
        is_calculation = True if "calculation" in source else False
        url = source["url"] if "url" in source else ""
        if "facts" not in source:
            continue
        for fact in source["facts"]:
            keys = [key for key in fact if key not in ["reference", "comment", "source_id"]]
            for key in keys:
                if key not in facts:
                    facts[key] = []
                facts[key].append(Fact(company, url, is_calculation, fact[key]))


def populate_raw_facts(
    all_facts: dict[str, list[Fact]], company: str, facts: dict[str, float]
) -> None:
    """Extract all raw facts from list of facts dictionaries and adds to all facts dictionary"""
    for fact in facts:
        keys = [key for key in fact if key not in ["reference", "comment", "source_id"]]
        for key in keys:
            if key not in all_facts:
                all_facts[key] = []
            # TODO fix calc
            all_facts[key].append(Fact(company, "", False, fact[key]))  # type: ignore


def get_all_facts() -> dict[str, list[Fact]]:
    """Extract all facts from all yaml files under data"""
    facts: dict[str, list[Fact]] = {}
    files = glob("data/**/*.yaml", recursive=True)
    for file in files:
        with open(file, "r") as stream:
            document = yaml.safe_load(stream)
            pth = Path(file)
            if "company" in document and "sources" in document["company"]:
                populate_facts(facts, "/".join(pth.parts[-2:]), document["company"]["sources"])
            if "sources" in document:
                populate_facts(facts, "/".join(pth.parts[-2:]), document["sources"])
            if "facts" in document:
                populate_raw_facts(facts, "/".join(pth.parts[-2:]), document["facts"])
            if "products" in document:
                for product in document["products"]:
                    if "facts" in product:
                        populate_raw_facts(facts, "/".join(pth.parts[-2:]), product["facts"])
            if "properties" in document:
                for publisher_property in document["properties"]:
                    populate_raw_facts(facts, "/".join(pth.parts[-2:]), publisher_property["facts"])
    return facts
