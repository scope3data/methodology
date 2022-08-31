import logging
from glob import glob
from pathlib import Path

import yaml
from yaml.loader import SafeLoader


class Fact:
    """A fact from one of our sources"""

    def __init__(self, company: str, url: str | None, is_calculation: bool, value: float) -> None:
        self.company = company
        self.url = "n/a" if not url else url
        self.is_calculation = is_calculation
        self.value = value

    def __repr__(self):
        return f"{self.company}{' (calculation)' if self.is_calculation else ''}: {self.value}"


def log_step(key: str, value: str, source: str, depth: int) -> None:
    logging.info(f"{'  ' * depth}{key} = {value} ({source})")


def log_result(key: str, value: str, depth: int) -> None:
    logging.info(f"{'  ' * (depth - 1)}-------------------------------------------")
    logging.info(f"{'  ' * depth}{key} = {value} (calculation)")


def get_fact_or_default(
    key: str, facts: dict[str, float], defaults: dict[str, float] | None, depth: int
) -> float:
    if key in facts:
        log_step(key, str(facts[key]), "fact", depth)
        return facts[key]
    if defaults is not None and key in defaults:
        log_step(key, str(defaults[key]), "default", depth)
        return defaults[key]
    raise Exception(f"No default found for '{key}'")


def get_facts_from_sources(sources) -> dict[str, float]:
    facts: dict[str, float] = {}
    for source in sources:
        for fact in source["facts"]:
            keys = [key for key in fact if key != "reference" and key != "comment"]
            for key in keys:
                facts[key] = fact[key]
    return facts


def populate_facts(facts: dict[str, list[Fact]], company: str, sources) -> None:
    for source in sources:
        is_calculation = True if "calculation" in source else False
        url = source["url"] if "url" in source else ""
        if "facts" not in source:
            continue
        for fact in source["facts"]:
            keys = [key for key in fact if key != "reference" and key != "comment"]
            for key in keys:
                if key not in facts:
                    facts[key] = []
                facts[key].append(Fact(company, url, is_calculation, fact[key]))


def get_all_facts() -> dict[str, list[Fact]]:
    facts: dict[str, list[Fact]] = {}
    files = glob("sources/**/*.yaml", recursive=True)
    for file in files:
        stream = open(file, "r")
        document = yaml.load(stream, Loader=SafeLoader)
        pth = Path(file)
        if "company" in document and "sources" in document["company"]:
            populate_facts(facts, "/".join(pth.parts[-2:]), document["company"]["sources"])
        if "sources" in document:
            populate_facts(facts, "/".join(pth.parts[-2:]), document["sources"])
    return facts
