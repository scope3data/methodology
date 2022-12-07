""" Model for computing emissions related to networking """

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from scope3_methodology.api.input_models import NetworkingConnectionType
from scope3_methodology.utils.custom_base_model import CustomBaseModel


@dataclass
class ModeledDeviceNetworking:
    """Modeled networking information for a specific device and connection type"""

    device: str = field(metadata={"default_eligible": True})
    connection_type: NetworkingConnectionType = field(metadata={"default_eligible": True})
    power_usage_kwh_per_gb: Decimal = field(metadata={"default_eligible": True})


@dataclass
class NetworkingConnection(CustomBaseModel):
    """
    Raw emissions information about networking emissions for a connection type
    """

    generic_kwh_per_gb: Decimal = field(metadata={"default_eligible": True})
    kwh_per_gb_per_device: Optional[dict[str, Decimal]] = field(
        default=None, metadata={"default_eligible": True}
    )

    def get_power_usage_kwh_per_gb(self, device: str):
        """Get the networking kwh_per_gb for a specific device"""
        if self.kwh_per_gb_per_device and device in self.kwh_per_gb_per_device:
            return round(self.kwh_per_gb_per_device[device], 5)
        return round(self.generic_kwh_per_gb, 5)

    def model_device(
        self, device: str, connection: NetworkingConnectionType
    ) -> ModeledDeviceNetworking | None:
        """
        Model networking emissions based on the provided device
        :return: ModeledNetworking
        """

        return ModeledDeviceNetworking(
            device,
            connection,
            self.get_power_usage_kwh_per_gb(device),
        )
