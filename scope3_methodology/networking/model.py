""" Model for computing emissions related to networking """

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from scope3_methodology.api.input_models import NetworkingConnectionType
from scope3_methodology.networking.transmission_rate_model import TransmissionRate
from scope3_methodology.utils.custom_base_model import CustomBaseModel


@dataclass
class ModeledDeviceNetworking:
    """
    Modeled conventional networking information for a specific device and connection type
    and power modeled streaming energy usage for a specific device, connection type,
    and transmission rate
    """

    device: str
    connection_type: NetworkingConnectionType
    conventional_model_power_usage_kwh_per_gb: Decimal
    power_model_energy_usage_kwh_per_second: Optional[Decimal]
    power_model_transmission_rate: Optional[TransmissionRate]


@dataclass
class NetworkingConnection(CustomBaseModel):
    """
    Raw emissions information about networking emissions for a connection type
    """

    conventional_model_generic_kwh_per_gb: Decimal = field(metadata={"default_eligible": True})
    conventional_model_kwh_per_gb_per_device: Optional[dict[str, Decimal]] = field(
        default=None, metadata={"default_eligible": True}
    )
    streaming_resolution_per_device: Optional[dict[str, str]] = field(
        default=None, metadata={"default_eligible": True}
    )
    power_model_constant_watt: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    power_model_variable_watt_per_mbps: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    power_model_constant_watt_per_device: Optional[dict[str, Decimal]] = field(
        default=None, metadata={"default_eligible": True}
    )
    power_model_variable_watt_per_mbps_per_device: Optional[dict[str, Decimal]] = field(
        default=None, metadata={"default_eligible": True}
    )

    def get_power_usage_kwh_per_gb(self, device: str):
        """Get the networking kwh_per_gb for a specific device"""
        if (
            self.conventional_model_kwh_per_gb_per_device
            and device in self.conventional_model_kwh_per_gb_per_device
        ):
            return round(self.conventional_model_kwh_per_gb_per_device[device], 5)
        return round(self.conventional_model_generic_kwh_per_gb, 5)

    def get_power_model_constant_watt(self, device: str) -> Decimal | None:
        """Get the networking power_model_constant_watt for a specific device"""
        if (
            self.power_model_constant_watt_per_device
            and device in self.power_model_constant_watt_per_device
        ):
            return self.power_model_constant_watt_per_device[device]
        return self.power_model_constant_watt

    def get_power_model_variable_watt_per_mbps(self, device: str) -> Decimal | None:
        """Get the networking power_model_variable_watt_per_mbps for a specific device"""
        if (
            self.power_model_variable_watt_per_mbps_per_device
            and device in self.power_model_variable_watt_per_mbps_per_device
        ):
            return self.power_model_variable_watt_per_mbps_per_device[device]
        return self.power_model_variable_watt_per_mbps

    def calculate_power_energy_usage_kwh_per_second(
        self, device: str, quality_transmission_rate: Optional[TransmissionRate]
    ):
        """Calculate the power streaming energy usage based on quality transmission rate"""
        power_model_constant_watt = self.get_power_model_constant_watt(device)
        power_model_variable_watt_per_mbps = self.get_power_model_variable_watt_per_mbps(device)

        if (
            quality_transmission_rate
            and power_model_constant_watt
            and power_model_variable_watt_per_mbps
        ):
            return (
                (
                    power_model_constant_watt
                    + (
                        power_model_variable_watt_per_mbps
                        * quality_transmission_rate.transmission_rate_mbps
                    )
                )
                / Decimal("1000")
                / Decimal("3600")
            )
        return None

    def model_device(
        self,
        device: str,
        connection: NetworkingConnectionType,
        transmission_rate: Optional[TransmissionRate],
    ) -> ModeledDeviceNetworking | None:
        """
        Model conventional networking emissions based on the provided device, and
        power model streaming energy by device, connection, and duration
        :return: ModeledNetworking
        """
        power_energy_usage_kwh_per_second = self.calculate_power_energy_usage_kwh_per_second(
            device, transmission_rate
        )

        return ModeledDeviceNetworking(
            device,
            connection,
            self.get_power_usage_kwh_per_gb(device),
            power_energy_usage_kwh_per_second,
            transmission_rate if power_energy_usage_kwh_per_second else None,
        )
