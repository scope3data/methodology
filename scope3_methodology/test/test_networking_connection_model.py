""" Tests for networking connection emissions model """
import unittest
from decimal import Decimal

from scope3_methodology.api.input_models import (
    EndUserDevices,
    NetworkingConnectionType,
    PropertyChannel,
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
    StreamingResolution.HIGH.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.STREAMING_VIDEO.value,
)


class TestNetworkingConnection(unittest.TestCase):
    """Test EndUserDeviceModel functions"""

    def test_networking_connection_conventional_model(self):
        """Test networking connection conventional model calculations"""
        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.MOBILE.value, TEST_DEFAULTS_FILE
        )
        for device in EndUserDevices:
            self.assertEqual(
                mobile_networking_connection.model_device_conventional_model(
                    device.value,
                    NetworkingConnectionType.MOBILE,
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.MOBILE,
                    conventional_model_power_usage_kwh_per_gb=Decimal("0.14"),
                    power_model_transmission_rate=None,
                    power_model_energy_usage_kwh_per_second=None,
                    channel=None,
                ),
            )

        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.FIXED.value, TEST_DEFAULTS_FILE
        )
        for device in EndUserDevices:
            self.assertEqual(
                mobile_networking_connection.model_device_conventional_model(
                    device.value,
                    NetworkingConnectionType.FIXED,
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.FIXED,
                    conventional_model_power_usage_kwh_per_gb=Decimal("0.030"),
                    power_model_transmission_rate=None,
                    power_model_energy_usage_kwh_per_second=None,
                    channel=None,
                ),
            )

        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.UNKNOWN.value, TEST_DEFAULTS_FILE
        )
        for device in EndUserDevices:
            if device == EndUserDevices.SMARTPHONE:
                self.assertEqual(
                    mobile_networking_connection.model_device_conventional_model(
                        device.value,
                        NetworkingConnectionType.UNKNOWN,
                    ),
                    ModeledDeviceNetworking(
                        device=device.value,
                        connection_type=NetworkingConnectionType.UNKNOWN,
                        conventional_model_power_usage_kwh_per_gb=Decimal("0.14"),
                        power_model_transmission_rate=None,
                        power_model_energy_usage_kwh_per_second=None,
                        channel=None,
                    ),
                )
            else:
                self.assertEqual(
                    mobile_networking_connection.model_device_conventional_model(
                        device.value,
                        NetworkingConnectionType.UNKNOWN,
                    ),
                    ModeledDeviceNetworking(
                        device=device.value,
                        connection_type=NetworkingConnectionType.UNKNOWN,
                        conventional_model_power_usage_kwh_per_gb=Decimal("0.030"),
                        power_model_transmission_rate=None,
                        power_model_energy_usage_kwh_per_second=None,
                        channel=None,
                    ),
                )

    def test_networking_connection_mobile_power_model(self):
        """Test power networking connection model calculations for mobile connection type"""
        mobile_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.MOBILE.value, TEST_DEFAULTS_FILE
        )
        self.assertEqual(
            mobile_networking_connection,
            NetworkingConnection(
                conventional_model_generic_kwh_per_gb=Decimal("0.14"),
                conventional_model_kwh_per_gb_per_device=None,
                power_model_constant_watt=Decimal("1.2"),
                power_model_variable_watt_per_mbps=Decimal("1.53"),
                transmission_rate_quality_per_channel_per_device={
                    PropertyChannel.STREAMING_VIDEO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.ULTRA.value,
                    },
                    PropertyChannel.DIGITAL_AUDIO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.HIGH.value,
                    },
                },
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                mobile_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.14"),
            )
            self.assertEqual(
                mobile_networking_connection.model_device_power_model(
                    device.value,
                    NetworkingConnectionType.MOBILE,
                    TEST_TRANSMISSION_RATE,
                    PropertyChannel.STREAMING_VIDEO.value,
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.MOBILE,
                    conventional_model_power_usage_kwh_per_gb=None,
                    power_model_transmission_rate=TEST_TRANSMISSION_RATE,
                    power_model_energy_usage_kwh_per_second=Decimal(
                        "0.000003168083333333333333333333333"
                    ),
                    channel=PropertyChannel.STREAMING_VIDEO.value,
                ),
            )

    def test_networking_connection_fixed_power_model(self):
        """Test power networking connection model calculations for fixed connection type"""
        fixed_networking_connection = NetworkingConnection.load_default_yaml(
            NetworkingConnectionType.FIXED.value, TEST_DEFAULTS_FILE
        )
        print(fixed_networking_connection)
        self.assertEqual(
            fixed_networking_connection,
            NetworkingConnection(
                conventional_model_generic_kwh_per_gb=Decimal("0.0300000"),
                conventional_model_kwh_per_gb_per_device=None,
                power_model_constant_watt=Decimal("9.550000000"),
                power_model_variable_watt_per_mbps=Decimal("0.03"),
                transmission_rate_quality_per_channel_per_device={
                    PropertyChannel.STREAMING_VIDEO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.ULTRA.value,
                    },
                    PropertyChannel.DIGITAL_AUDIO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.HIGH.value,
                    },
                },
            ),
        )

        for device in EndUserDevices:
            self.assertEqual(
                fixed_networking_connection.get_power_usage_kwh_per_gb(device.value),
                Decimal("0.030"),
            )
            self.assertEqual(
                fixed_networking_connection.model_device_power_model(
                    device.value,
                    NetworkingConnectionType.FIXED,
                    TEST_TRANSMISSION_RATE,
                    PropertyChannel.STREAMING_VIDEO.value,
                ),
                ModeledDeviceNetworking(
                    device=device.value,
                    connection_type=NetworkingConnectionType.FIXED,
                    conventional_model_power_usage_kwh_per_gb=None,
                    power_model_transmission_rate=TEST_TRANSMISSION_RATE,
                    power_model_energy_usage_kwh_per_second=Decimal(
                        "0.000002708361111111111111111111111"
                    ),
                    channel=PropertyChannel.STREAMING_VIDEO.value,
                ),
            )

    def test_networking_connection_unknown_power_model(self):
        """Test power networking connection model calculations for unknown connection type"""
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
                power_model_constant_watt_per_device={
                    "personal_computer": Decimal("9.55"),
                    "smartphone": Decimal("1.200000000"),
                    "tablet": Decimal("9.55"),
                    "tv_system": Decimal("9.55"),
                },
                power_model_variable_watt_per_mbps_per_device={
                    "personal_computer": Decimal("0.030000000"),
                    "smartphone": Decimal("1.530000000"),
                    "tablet": Decimal("0.030000000"),
                    "tv_system": Decimal("0.030000000"),
                },
                transmission_rate_quality_per_channel_per_device={
                    PropertyChannel.STREAMING_VIDEO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.ULTRA.value,
                    },
                    PropertyChannel.DIGITAL_AUDIO.value: {
                        EndUserDevices.PERSONAL_COMPUTER.value: StreamingResolution.HIGH.value,
                        EndUserDevices.SMARTPHONE.value: StreamingResolution.MEDIUM.value,
                        EndUserDevices.TABLET.value: StreamingResolution.HIGH.value,
                        EndUserDevices.TV_SYSTEM.value: StreamingResolution.HIGH.value,
                    },
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
            Decimal("0.030"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(
                EndUserDevices.PERSONAL_COMPUTER.value
            ),
            Decimal("0.030"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb(
                EndUserDevices.TV_SYSTEM.value
            ),
            Decimal("0.030"),
        )
        self.assertEqual(
            unknown_networking_connection.get_power_usage_kwh_per_gb("unknown"),
            Decimal("0.10"),
        )

        self.assertEqual(
            unknown_networking_connection.model_device_power_model(
                "unknown",
                NetworkingConnectionType.UNKNOWN,
                TEST_TRANSMISSION_RATE,
                PropertyChannel.STREAMING_VIDEO.value,
            ),
            ModeledDeviceNetworking(
                device="unknown",
                connection_type=NetworkingConnectionType.UNKNOWN,
                conventional_model_power_usage_kwh_per_gb=None,
                power_model_transmission_rate=None,
                power_model_energy_usage_kwh_per_second=None,
                channel=None,
            ),
        )

        self.assertEqual(
            unknown_networking_connection.model_device_power_model(
                EndUserDevices.PERSONAL_COMPUTER.value,
                NetworkingConnectionType.UNKNOWN,
                TEST_TRANSMISSION_RATE,
                PropertyChannel.STREAMING_VIDEO.value,
            ),
            ModeledDeviceNetworking(
                device=EndUserDevices.PERSONAL_COMPUTER.value,
                connection_type=NetworkingConnectionType.UNKNOWN,
                conventional_model_power_usage_kwh_per_gb=None,
                power_model_transmission_rate=TEST_TRANSMISSION_RATE,
                power_model_energy_usage_kwh_per_second=Decimal(
                    "0.000002708361111111111111111111111"
                ),
                channel=PropertyChannel.STREAMING_VIDEO.value,
            ),
        )


if __name__ == "__main__":
    unittest.main()
