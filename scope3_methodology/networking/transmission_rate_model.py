""" Model for transmission rate """


from dataclasses import dataclass, field
from decimal import Decimal

from scope3_methodology.utils.custom_base_model import CustomBaseModel


@dataclass
class TransmissionRate(CustomBaseModel):
    """
    Transmission rate mbps for a specific resolution
    """

    name: str = field(metadata={"default_eligible": True})
    resolution: str = field(metadata={"default_eligible": True})
    transmission_rate_mbps: Decimal = field(metadata={"default_eligible": True})
