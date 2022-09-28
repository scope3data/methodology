#!/usr/bin/env python
""" ATP Model Helpers """
from decimal import Decimal

from scope3_methodology.utils.utils import log_step


def get_product_info(
    key: str, default: Decimal | None, product: dict[str, str], depth: int
) -> str | Decimal:
    """Find product information for a specific key or raise exception"""
    if key in product:
        log_step(key, product[key], "", depth)
        return product[key]
    if default is not None:
        log_step(key, default, "default", depth)
        return default
    raise Exception(
        f"No value found in product {product['name'] if 'name' in product else ''} for '{key}'"
    )
