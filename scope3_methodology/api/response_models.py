""" API Response Models """
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ATPDefaultsResponse(BaseModel):
    """Response for /defaults/atp/{template}"""

    template: str
    corporate_emissions_g_co2e_per_bid_request: Optional[Decimal]
    adtech_platform_block_rate: Decimal = Decimal("0.0")
    publisher_block_rate: Decimal = Decimal("0.0")


class PropertyDefaultsResponse(BaseModel):
    """Response for /defaults/property/{channel}"""

    channel: str
    template: str
    corporate_emissions_g_co2e_per_impression: Optional[Decimal]
    quality_impressions_per_duration_s: Optional[Decimal]
