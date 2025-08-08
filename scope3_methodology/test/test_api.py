""" Tests for API startup and endpoints """

import unittest
from decimal import Decimal

from scope3_methodology.api.api import (
    adtech_platform_defaults,
    docs_defaults,
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
TEST_TRANSMISSION_RATE_DEFAULTS_FILE = "defaults/transmission_rate-defaults.yaml"
TEST_DOCS_DEFAULTS_FILE = "defaults/docs-defaults.yaml"
TEST_BROADCASTING_DEFAULTS_FILE = "defaults/broadcasting-defaults.yaml"

TEST_TRANSMISSION_RATE_HIGH = TransmissionRate.load_default_yaml(
    StreamingResolution.HIGH.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.STREAMING_VIDEO.value,
)
TEST_TRANSMISSION_RATE_LOW = TransmissionRate.load_default_yaml(
    StreamingResolution.LOW.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.STREAMING_VIDEO.value,
)
TEST_TRANSMISSION_RATE_ULTRA = TransmissionRate.load_default_yaml(
    StreamingResolution.ULTRA.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.STREAMING_VIDEO.value,
)
TEST_TRANSMISSION_RATE_MEDIUM = TransmissionRate.load_default_yaml(
    StreamingResolution.MEDIUM.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.STREAMING_VIDEO.value,
)

TEST_TRANSMISSION_RATE_CB_HIGH = TransmissionRate.load_default_yaml(
    StreamingResolution.HIGH.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.CTV_BVOD.value,
)
TEST_TRANSMISSION_RATE_CB_LOW = TransmissionRate.load_default_yaml(
    StreamingResolution.LOW.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.CTV_BVOD.value,
)
TEST_TRANSMISSION_RATE_CB_ULTRA = TransmissionRate.load_default_yaml(
    StreamingResolution.ULTRA.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.CTV_BVOD.value,
)
TEST_TRANSMISSION_RATE_CB_MEDIUM = TransmissionRate.load_default_yaml(
    StreamingResolution.MEDIUM.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.CTV_BVOD.value,
)

TEST_TRANSMISSION_RATE_DA_HIGH = TransmissionRate.load_default_yaml(
    StreamingResolution.HIGH.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.DIGITAL_AUDIO.value,
)
TEST_TRANSMISSION_RATE_DA_MEDIUM = TransmissionRate.load_default_yaml(
    StreamingResolution.MEDIUM.value,
    TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
    PropertyChannel.DIGITAL_AUDIO.value,
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
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
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
            Decimal("0.090940000"),
        )
        self.assertEqual(
            organization_defaults[OrganizationType.PUBLISHER].revenue_allocation_to_digital_ads_pct,
            Decimal("11.698000000"),
        )
        self.assertTrue(organization_defaults[OrganizationType.GENERIC])
        self.assertEqual(
            organization_defaults[
                OrganizationType.GENERIC
            ].travel_emissions_mt_co2e_per_employee_per_month,
            Decimal("0.077616667"),
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

        self.assertEqual(len(property_defaults), 8)
        self.assertTrue(property_defaults[PropertyChannel.DISPLAY])
        self.assertEqual(
            property_defaults[PropertyChannel.DISPLAY].quality_impressions_per_duration_s,
            Decimal("0.1"),
        )
        self.assertTrue(property_defaults[PropertyChannel.DISPLAY_WEB])
        self.assertEqual(
            property_defaults[PropertyChannel.DISPLAY_WEB].quality_impressions_per_duration_s,
            Decimal("0.1"),
        )
        self.assertTrue(property_defaults[PropertyChannel.DISPLAY_APP])
        self.assertEqual(
            property_defaults[PropertyChannel.DISPLAY_APP].quality_impressions_per_duration_s,
            Decimal("0.1"),
        )
        self.assertTrue(property_defaults[PropertyChannel.STREAMING])
        self.assertEqual(
            property_defaults[PropertyChannel.STREAMING].quality_impressions_per_duration_s,
            Decimal("0.0032"),
        )
        self.assertTrue(property_defaults[PropertyChannel.STREAMING_VIDEO])
        self.assertEqual(
            property_defaults[PropertyChannel.STREAMING_VIDEO].quality_impressions_per_duration_s,
            Decimal("0.0032"),
        )
        self.assertTrue(property_defaults[PropertyChannel.CTV_BVOD])
        self.assertEqual(
            property_defaults[PropertyChannel.CTV_BVOD].quality_impressions_per_duration_s,
            Decimal("0.0032"),
        )
        self.assertTrue(property_defaults[PropertyChannel.SOCIAL])
        self.assertEqual(
            property_defaults[PropertyChannel.SOCIAL].quality_impressions_per_duration_s,
            Decimal("0.1"),
        )
        self.assertTrue(property_defaults[PropertyChannel.DIGITAL_AUDIO])
        self.assertEqual(
            property_defaults[PropertyChannel.DIGITAL_AUDIO].quality_impressions_per_duration_s,
            Decimal("0.0032"),
        )

        self.assertEqual(len(end_user_device_defaults), 5)
        self.assertTrue(end_user_device_defaults[EndUserDevices.SMART_SPEAKER])
        self.assertEqual(
            end_user_device_defaults[EndUserDevices.SMART_SPEAKER].draw_watts,
            Decimal("2.5"),
        )
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

        sv_tr = transmission_rate_defaults[PropertyChannel.STREAMING_VIDEO]
        self.assertEqual(len(sv_tr), 4)
        self.assertEqual(
            sv_tr[StreamingResolution.HIGH].transmission_rate_mbps,
            Decimal("6.67"),
        )
        self.assertEqual(
            sv_tr[StreamingResolution.MEDIUM].transmission_rate_mbps,
            Decimal("2.22"),
        )
        self.assertEqual(
            sv_tr[StreamingResolution.LOW].transmission_rate_mbps,
            Decimal("0.56"),
        )
        self.assertEqual(
            sv_tr[StreamingResolution.ULTRA].transmission_rate_mbps,
            Decimal("15.56"),
        )

        da_tr = transmission_rate_defaults[PropertyChannel.DIGITAL_AUDIO]
        self.assertEqual(len(da_tr), 3)
        self.assertEqual(
            da_tr[StreamingResolution.HIGH].transmission_rate_mbps,
            Decimal("0.16"),
        )
        self.assertEqual(
            da_tr[StreamingResolution.MEDIUM].transmission_rate_mbps,
            Decimal("0.096"),
        )
        self.assertEqual(
            da_tr[StreamingResolution.LOW].transmission_rate_mbps,
            Decimal("0.024"),
        )

        docs_defs = docs_defaults
        self.assertEqual(len(docs_defs), 46)

    def test_get_all_con_networking_connection_device_fixed_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.FIXED
                and device_network_connection.channel is None
            ):
                self.assertEqual(
                    device_network_connection.conventional_model_power_usage_kwh_per_gb,
                    Decimal("0.030"),
                )

    def test_get_all_power_networking_connection_device_fixed_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.FIXED
                and device_network_connection.channel == PropertyChannel.DIGITAL_AUDIO.value
            ):
                if device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002653577777777777777777777778"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002654111111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_HIGH,
                    )
            if (
                device_network_connection.connection_type == NetworkingConnectionType.FIXED
                and device_network_connection.channel == PropertyChannel.CTV_BVOD.value
            ):
                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002782444444444444444444444444"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002671277777777777777777777778"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002708361111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_HIGH,
                    )
            if (
                device_network_connection.connection_type == NetworkingConnectionType.FIXED
                and device_network_connection.channel == PropertyChannel.STREAMING_VIDEO.value
            ):
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

    def test_get_all_con_networking_connection_device_unknown_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.UNKNOWN
                and device_network_connection.channel is None
            ):
                if device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.conventional_model_power_usage_kwh_per_gb,
                        Decimal("0.14"),
                    )
                elif device_network_connection.device == EndUserDevices.SMART_SPEAKER.value:
                    self.assertEqual(
                        device_network_connection.conventional_model_power_usage_kwh_per_gb,
                        Decimal("0.1"),
                    )
                else:
                    self.assertEqual(
                        device_network_connection.conventional_model_power_usage_kwh_per_gb,
                        Decimal("0.030"),
                    )

    def test_get_all_power_networking_connection_device_unknown_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.UNKNOWN
                and device_network_connection.channel == PropertyChannel.DIGITAL_AUDIO.value
            ):
                if device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("3.741333333333333333333333333E-7"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002654111111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_HIGH,
                    )
            if (
                device_network_connection.connection_type == NetworkingConnectionType.UNKNOWN
                and device_network_connection.channel == PropertyChannel.CTV_BVOD.value
            ):
                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002782444444444444444444444444"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000001276833333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000002708361111111111111111111111"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_HIGH,
                    )
            if (
                device_network_connection.connection_type == NetworkingConnectionType.UNKNOWN
                and device_network_connection.channel == PropertyChannel.STREAMING_VIDEO.value
            ):
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

    def test_get_all_conventional_networking_connection_device_mobile_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.MOBILE
                and device_network_connection.channel is None
            ):
                self.assertEqual(
                    device_network_connection.conventional_model_power_usage_kwh_per_gb,
                    Decimal("0.14"),
                )

    def test_get_all_power_networking_connection_device_mobile_defaults(self):
        """Test get_all_networking_connection_device_defaults returns expected output"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
            TEST_NETWORKING_DEFAULTS_FILE,
            TEST_TRANSMISSION_RATE_DEFAULTS_FILE,
            TEST_DOCS_DEFAULTS_FILE,
        )

        response = get_all_networking_connection_device_defaults()
        self.assertEqual(len(response), 51)

        for device_network_connection in response:
            if (
                device_network_connection.connection_type == NetworkingConnectionType.MOBILE
                and device_network_connection.channel == PropertyChannel.DIGITAL_AUDIO.value
            ):
                if device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("3.741333333333333333333333333E-7"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("4.013333333333333333333333333E-7"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_DA_HIGH,
                    )
            if (
                device_network_connection.connection_type == NetworkingConnectionType.MOBILE
                and device_network_connection.channel == PropertyChannel.STREAMING_VIDEO.value
            ):
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

            if (
                device_network_connection.connection_type == NetworkingConnectionType.MOBILE
                and device_network_connection.channel == PropertyChannel.CTV_BVOD.value
            ):
                if device_network_connection.device == EndUserDevices.TV_SYSTEM.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000006946333333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_ULTRA,
                    )
                elif device_network_connection.device == EndUserDevices.SMARTPHONE.value:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000001276833333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_MEDIUM,
                    )
                else:
                    self.assertEqual(
                        device_network_connection.power_model_energy_usage_kwh_per_second,
                        Decimal("0.000003168083333333333333333333333"),
                    )
                    self.assertEqual(
                        device_network_connection.power_model_transmission_rate,
                        TEST_TRANSMISSION_RATE_CB_HIGH,
                    )

    # TODO add in testing for API endpoints issue: #53


if __name__ == "__main__":
    unittest.main()
