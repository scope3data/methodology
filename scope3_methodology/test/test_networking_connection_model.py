""" Tests for networking connection emissions model """
import unittest
from decimal import Decimal

from scope3_methodology.api.input_models import (
    EndUserDevices,
    NetworkingConnectionType,
    StreamingResolution,
)
from scope3_methodology.networking.model import (
    ModeledDeviceNetworking,
    NetworkingConnection,
)
from scope3_methodology.networking.transmission_rate_model import TransmissionRate

TEST_DEFAULTS_FILE = "defaults/networking-defaults.yaml"
TEST_TRANSMISSION_RATE_DEFAULTS_FILE = "defaults/transmission_rate-defaults.yaml"

TEST_TRANSMISSION_RATE = TransmissionRate.load_default_yaml(
    StreamingResolution.HIGH.value, TEST_TRANSMISSION_RATE_DEFAULTS_FILE
)


class TestNetworkingConnection(unittest.TestCase):
    """Test EndUserDeviceModel functions"""

    def test_networking_connection_unknown(self):
        """Test load unknown defaults"""
        unknown_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.UNKNOWN.value, TEST_DEFAULTS_FILE
        )
        self.assertEqual(
            unknown_networking_connection,
            NetworkingConnection(
                conventional_model_generic_kwh_per_gb=Decimal("0.100000000"),
                conventional_model_kwh_per_gb_per_device={
                    "personal_computer": Decimal("0.030000000"),
                    "smartphone": Decimal("0.140000000"),
                    "tablet": Decimal("0.030000000"),
                    "tv_system": Decimal("0.030000000"),
                },
            ),
        )

        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(
                EndUserDevices.SMARTPHONE.value
            ),
            Decimal("0.14000"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(EndUserDevices.TABLET.value),
            Decimal("0.03"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(
                EndUserDevices.PERSONAL_COMPUTER.value
            ),
            Decimal("0.03"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(
                EndUserDevices.TV_SYSTEM.value
            ),
            Decimal("0.03"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb("unknown"),
            Decimal("0.10"),
        )

        self.assertEqual(
            unknown_networking_connection.model_device(
                "unknown", NetworkingConnectionType.UNKNOWN, TEST_TRANSMISSION_RATE
            ),
            ModeledDeviceNetworking(
                device="unknown",
                connection_type=NetworkingConnectionType.UNKNOWN,
                conventional_model_power_usage_kwh_per_gb=Decimal("0.10"),
                power_model_transmission_rate=None,
                power_model_energy_usage_kwh_per_second=None,
            ),
        )

        self.assertEqual(
            unknown_networking_connection.model_device(
                EndUserDevices.PERSONAL_COMPUTER.value,
                NetworkingConnectionType.UNKNOWN,
                TEST_TRANSMISSION_RATE,
            ),
            ModeledDeviceNetworking(
                device=EndUserDevices.PERSONAL_COMPUTER.value,
                connection_type=NetworkingConnectionType.UNKNOWN,
                conventional_model_power_usage_kwh_per_gb=Decimal("0.03"),
                power_model_transmission_rate=None,
                power_model_energy_usage_kwh_per_second=None,
            ),
        )

    def test_networking_connection_mobile(self):
        """Test load unknown defaults"""
        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.MOBILE.value, TEST_DEFAULTS_FILE
        )
        print(mobile_networking_connection)
        self.assertEqual(
            mobile_networking_connection,
            NetworkingConnection(
                conventional_model_generic_kwh_per_gb=Decimal("0.14"),
                conventional_model_kwh_per_gb_per_device=None,
                power_model_constant_watt=Decimal("1.2"),
                power_model_variable_watt_per_mbps=Decimal("1.53"),
                streaming_resolution_per_device={
                    EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                    EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                    EndUserDevices.TV_SYSTEM.value: StreamingResolution.ULTRA.value,
                    EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                },
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                mobile_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.14"),
            )
            self.assertEqual(
                mobile_networking_connection.model_device(
                    device.value, NetworkingConnectionType.MOBILE, TEST_TRANSMISSION_RATE
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.MOBILE,
                    conventional_model_power_usage_kwh_per_gb=Decimal("0.14"),
                    power_model_transmission_rate=TEST_TRANSMISSION_RATE,
                    power_model_energy_usage_kwh_per_second=Decimal(
                        "0.000003168083333333333333333333333"
                    ),
                ),
            )

    def test_networking_connection_fixed(self):
        """Test load unknown defaults"""
        fixed_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.FIXED.value, TEST_DEFAULTS_FILE
        )
        self.assertEqual(
            fixed_networking_connection,
            NetworkingConnection(
                conventional_model_generic_kwh_per_gb=Decimal("0.03"),
                conventional_model_kwh_per_gb_per_device=None,
                power_model_constant_watt=Decimal("9.55"),
                power_model_variable_watt_per_mbps=Decimal("0.03"),
                streaming_resolution_per_device={
                    EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                    EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                    EndUserDevices.TV_SYSTEM.value: StreamingResolution.ULTRA.value,
                    EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                },
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                fixed_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.03"),
            )
            self.assertEqual(
                fixed_networking_connection.model_device(
                    device.value, NetworkingConnectionType.FIXED, TEST_TRANSMISSION_RATE
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.FIXED,
                    conventional_model_power_usage_kwh_per_gb=Decimal("0.03"),
                    power_model_transmission_rate=TEST_TRANSMISSION_RATE,
                    power_model_energy_usage_kwh_per_second=Decimal(
                        "0.000002708361111111111111111111111"
                    ),
                ),
            )


if __name__ == "__main__":
    unittest.main()
