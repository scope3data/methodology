from utils import get_fact_or_default, log_result


def get_corporate_keys() -> set[str]:
    return {
        "corporate emissions mt per month",
        "office emissions mt per employee per month",
        "travel emissions mt per employee per month",
        "overhead emissions mt per employee per month",
        "commuting emissions mt per employee per month",
    }


def get_corporate_emissions(
    facts: dict[str, float], defaults: dict[str, float], depth: int
) -> float:
    if "corporate emissions mt per month" in facts:
        return get_fact_or_default("corporate emissions mt per month", facts, defaults, depth)
    if "employees" not in facts:
        raise Exception("Must provide either 'corporate emissions mt per month' or 'employees'")
    officeEmissionsPerEmployee = get_fact_or_default(
        "office emissions mt per employee per month", facts, defaults, depth - 1
    )
    travelEmissionsPerEmployee = get_fact_or_default(
        "travel emissions mt per employee per month", facts, defaults, depth - 1
    )
    datacenterEmissionsPerEmployee = get_fact_or_default(
        "datacenter emissions mt per employee per month", facts, defaults, depth - 1
    )
    commutingEmissionsPerEmployee = get_fact_or_default(
        "commuting emissions mt per employee per month", facts, defaults, depth - 1
    )
    overheadEmissionsPerEmployee = get_fact_or_default(
        "overhead emissions mt per employee per month", facts, defaults, depth - 1
    )
    corporateEmissions = get_fact_or_default("employees", facts, defaults, depth - 1) * (
        officeEmissionsPerEmployee
        + travelEmissionsPerEmployee
        + commutingEmissionsPerEmployee
        + datacenterEmissionsPerEmployee
        + overheadEmissionsPerEmployee
    )
    log_result("corporate emissions mt per month", f"{corporateEmissions:.2f}", depth)
    return corporateEmissions
