#!/usr/bin/env python
""" ATP Model Helpers """
from utils.utils import log_step


def get_product_info(
    key: str, default: float | None, product: dict[str, str], depth: int
) -> str | float | None:
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
