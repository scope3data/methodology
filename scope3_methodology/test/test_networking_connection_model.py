""" Tests for networking connection emissions model """
import unittest
from decimal import Decimal

from scope3_methodology.api.input_models import EndUserDevices, NetworkingConnectionType
from scope3_methodology.networking.model import (
    ModeledDeviceNetworking,
    NetworkingConnection,
)

TEST_DEFAULTS_FILE = "defaults/networking-defaults.yaml"


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
                generic_kwh_per_gb=Decimal("0.100000000"),
                kwh_per_gb_per_device={
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
            unknown_networking_connection.model_device("unknown", NetworkingConnectionType.UNKNOWN),
            ModeledDeviceNetworking(
                device="unknown",
                connection_type=NetworkingConnectionType.UNKNOWN,
                power_usage_kwh_per_gb=Decimal("0.10"),
            ),
        )

        self.assertEqual(
            unknown_networking_connection.model_device(
                EndUserDevices.PERSONAL_COMPUTER.value, NetworkingConnectionType.UNKNOWN
            ),
            ModeledDeviceNetworking(
                device=EndUserDevices.PERSONAL_COMPUTER.value,
                connection_type=NetworkingConnectionType.UNKNOWN,
                power_usage_kwh_per_gb=Decimal("0.03"),
            ),
        )

    def test_networking_connection_mobile(self):
        """Test load unknown defaults"""
        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.MOBILE.value, TEST_DEFAULTS_FILE
        )
        self.assertEqual(
            mobile_networking_connection,
            NetworkingConnection(
                generic_kwh_per_gb=Decimal("0.14"),
                kwh_per_gb_per_device=None,
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                mobile_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.14"),
            )
            self.assertEqual(
                mobile_networking_connection.model_device(
                    device.value, NetworkingConnectionType.MOBILE
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.MOBILE,
                    power_usage_kwh_per_gb=Decimal("0.14"),
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
                generic_kwh_per_gb=Decimal("0.03"),
                kwh_per_gb_per_device=None,
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                fixed_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.03"),
            )
            self.assertEqual(
                fixed_networking_connection.model_device(
                    device.value, NetworkingConnectionType.FIXED
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.FIXED,
                    power_usage_kwh_per_gb=Decimal("0.03"),
                ),
            )


if __name__ == "__main__":
    unittest.main()
