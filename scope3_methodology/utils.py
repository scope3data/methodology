import logging


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
