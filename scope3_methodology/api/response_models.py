""" API Response Models """
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, PlainSerializer
from typing_extensions import Annotated


class ATPDefaultsResponse(BaseModel):
    """Response for /defaults/atp/{template}"""

    template: str
    corporate_emissions_g_co2e_per_bid_request: Annotated[
        Optional[Decimal],
        PlainSerializer(lambda x: float(x), return_type=float, when_used="json"),
    ]
    adtech_platform_block_rate: Annotated[
        Optional[Decimal],
        PlainSerializer(lambda x: float(x), return_type=float, when_used="json"),
    ] = 0.0
    publisher_block_rate: Annotated[
        Optional[Decimal],
        PlainSerializer(lambda x: float(x), return_type=float, when_used="json"),
    ] = 0.0


class PropertyDefaultsResponse(BaseModel):
    """Response for /defaults/property/{channel}"""

    channel: str
    template: str
    corporate_emissions_g_co2e_per_impression: Annotated[
        Optional[Decimal],
        PlainSerializer(lambda x: float(x), return_type=float, when_used="json"),
    ]
    quality_impressions_per_duration_s: Annotated[
        Optional[Decimal],
        PlainSerializer(lambda x: float(x), return_type=float, when_used="json"),
    ]
