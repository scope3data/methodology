""" Tests for API startup and endpoints """
import unittest
from decimal import Decimal

from scope3_methodology.api.api import (
    adtech_platform_defaults,
    end_user_device_defaults,
    get_all_networking_connection_device_defaults,
    load_default_files,
    organization_defaults,
    property_defaults,
    transmission_rate_defaults,
)
from scope3_methodology.api.input_models import (
    ATPTemplate,
    EndUserDevices,
    NetworkingConnectionType,
    OrganizationType,
    PropertyChannel,
    StreamingResolution,
)
from scope3_methodology.networking.transmission_rate_model import TransmissionRate

TEST_DEVICE_DEFAULTS_FILE = "defaults/end_user_device-defaults.yaml"
TEST_PROPERTY_DEFAULTS_FILE = "defaults/property-defaults.yaml"
TEST_ORGANIZATION_DEFAULTS_FILE = "defaults/organization-defaults.yaml"
TEST_ATP_DEFAULTS_FILE = "defaults/atp-defaults.yaml"
TEST_NETWORKING_DEFAULTS_FILE = "defaults/networking-defaults.yaml"
TEST_TRANSMISSION_RATES_DEFAULTS_FILE = "defaults/transmission_rate-defaults.yaml"

TEST_TRANSMISSION_RATE_DEFAULTS_FILE = "defaults/transmission_rate-defaults.yaml"

TEST_TRANSMISSION_RATE_HIGH = TransmissionRate.load_default_yaml(
    StreamingResolution.HIGH.value, TEST_TRANSMISSION_RATE_DEFAULTS_FILE
)
TEST_TRANSMISSION_RATE_LOW = TransmissionRate.load_default_yaml(
    StreamingResolution.LOW.value, TEST_TRANSMISSION_RATE_DEFAULTS_FILE
)
TEST_TRANSMISSION_RATE_ULTRA = TransmissionRate.load_default_yaml(
    StreamingResolution.ULTRA.value, TEST_TRANSMISSION_RATE_DEFAULTS_FILE
)
TEST_TRANSMISSION_RATE_MEDIUM = TransmissionRate.load_default_yaml(
    StreamingResolution.MEDIUM.value, TEST_TRANSMISSION_RATE_DEFAULTS_FILE
)


class TestAPI(unittest.TestCase):
    """Test API startup and endpoints"""

    def test_startup(self):
        """Test api startup loads defaults correctly"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATES_DEFAULTS_FILE,
        )

        # verify the correct count and a field that should be different across
        # all the different default types
        self.assertEqual(len(organization_defaults), 3)
        self.assertTrue(organization_defaults[OrganizationType.ATP])
        self.assertEqual(
            organization_defaults[
                OrganizationType.ATP
            ].travel_emissions_mt_co2e_per_employee_per_month,
            Decimal("0.011"),
        )
        self.assertTrue(organization_defaults[OrganizationType.PUBLISHER])
        self.assertEqual(
            organization_defaults[
                OrganizationType.PUBLISHER
            ].travel_emissions_mt_co2e_per_employee_per_month,
            Decimal("0.053"),
        )
        self.assertTrue(organization_defaults[OrganizationType.GENERIC])
        self.assertEqual(
            organization_defaults[
                OrganizationType.GENERIC
            ].travel_emissions_mt_co2e_per_employee_per_month,
            Decimal("0.0446"),
        )

        self.assertEqual(len(adtech_platform_defaults), 2)
        self.assertTrue(adtech_platform_defaults[ATPTemplate.DSP])
        self.assertEqual(
            adtech_platform_defaults[ATPTemplate.DSP].bid_requests_processed_billion_per_month,
            Decimal("38109"),
        )
        self.assertTrue(adtech_platform_defaults[ATPTemplate.SSP])
        self.assertEqual(
            adtech_platform_defaults[ATPTemplate.SSP].bid_requests_processed_billion_per_month,
            Decimal("6100.6"),
        )

        self.assertEqual(len(property_defaults), 2)
        self.assertTrue(property_defaults[PropertyChannel.DISPLAY])
        self.assertEqual(
            property_defaults[PropertyChannel.DISPLAY].quality_impressions_per_duration_s,
            Decimal("0.1"),
        )
        self.assertTrue(property_defaults[PropertyChannel.STREAMING])
        self.assertEqual(
            property_defaults[PropertyChannel.STREAMING].quality_impressions_per_duration_s,
            Decimal("0.0032"),
        )

        self.assertEqual(len(end_user_device_defaults), 4)
        self.assertTrue(end_user_device_defaults[EndUserDevices.SMARTPHONE])
        self.assertEqual(
            end_user_device_defaults[EndUserDevices.SMARTPHONE].draw_watts, Decimal("0.77")
        )
        self.assertTrue(end_user_device_defaults[EndUserDevices.PERSONAL_COMPUTER])
        self.assertEqual(
            end_user_device_defaults[EndUserDevices.PERSONAL_COMPUTER].draw_watts, Decimal("53.2")
        )
        self.assertTrue(end_user_device_defaults[EndUserDevices.TABLET])
        self.assertEqual(end_user_device_defaults[EndUserDevices.TABLET].draw_watts, Decimal("3"))
        self.assertTrue(end_user_device_defaults[EndUserDevices.TV_SYSTEM])
        self.assertEqual(
            end_user_device_defaults[EndUserDevices.TV_SYSTEM].draw_watts, Decimal("87.4")
        )

        self.assertEqual(len(transmission_rate_defaults), 4)
        self.assertEqual(
            transmission_rate_defaults[StreamingResolution.HIGH].transmission_rate_mbps,
            Decimal("6.67"),
        )
        self.assertEqual(
            transmission_rate_defaults[StreamingResolution.MEDIUM].transmission_rate_mbps,
            Decimal("2.22"),
        )
        self.assertEqual(
            transmission_rate_defaults[StreamingResolution.LOW].transmission_rate_mbps,
            Decimal("0.56"),
        )
        self.assertEqual(
            transmission_rate_defaults[StreamingResolution.ULTRA].transmission_rate_mbps,
            Decimal("15.56"),
        )

    def test_get_all_networking_connection_device_fixed_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATES_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 12)

        for device_network_connection in response:
            if device_network_connection.connection_type == NetworkingConnectionType.FIXED:
                self.assertEqual(
                    device_network_connection.conventional_model_power_usage_kwh_per_gb,
                    Decimal("0.03"),
                )
                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002782444444444444444444444444"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002671277777777777777777777778"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002708361111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_HIGH,
                    )

    def test_get_all_networking_connection_device_unknown_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATES_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 12)

        for device_network_connection in response:
            if device_network_connection.connection_type == NetworkingConnectionType.UNKNOWN:

                if device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.conventional_model_power_usage_kwh_per_gb,
                        Decimal("0.14"),
                    )
                else:
                    self.assertEqual(
                        device_network_connection.conventional_model_power_usage_kwh_per_gb,
                        Decimal("0.03"),
                    )

                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002782444444444444444444444444"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000001276833333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002708361111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_HIGH,
                    )

    def test_get_all_networking_connection_device_mobile_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATES_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 12)

        for device_network_connection in response:
            if device_network_connection.connection_type == NetworkingConnectionType.MOBILE:
                self.assertEqual(
                    device_network_connection.conventional_model_power_usage_kwh_per_gb,
                    Decimal("0.14"),
                )
                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000006946333333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000001276833333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000003168083333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_HIGH,
                    )

    # TODO add in testing for API endpoints issue: #53


if __name__ == "__main__":
    unittest.main()
