""" Model for transmission rate """

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from scope3_methodology.utils.custom_base_model import CustomBaseModel


@dataclass
class TransmissionRate(CustomBaseModel):
    """
    Transmission rate mbps for a specific resolution
    """

    channel: str = field(metadata={"default_eligible": True})
    name: str = field(metadata={"default_eligible": True})
    transmission_rate_mbps: Decimal = field(metadata={"default_eligible": True})
    resolution: Optional[str] = field(default=None, metadata={"default_eligible": True})
