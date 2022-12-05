""" Tests for API startup and endpoints """
import unittest
from decimal import Decimal

from scope3_methodology.api.api import (
    adtech_platform_defaults,
    end_user_device_defaults,
    load_default_files,
    organization_defaults,
    property_defaults,
)
from scope3_methodology.api.input_models import (
    ATPTemplate,
    EndUserDevices,
    OrganizationType,
    PropertyChannel,
)

TEST_DEVICE_DEFAULTS_FILE = "scope3_methodology/test/defaults/end_user_device-defaults.yaml"
TEST_PROPERTY_DEFAULTS_FILE = "scope3_methodology/test/defaults/property-defaults.yaml"
TEST_ORGANIZATION_DEFAULTS_FILE = "scope3_methodology/test/defaults/organization-defaults.yaml"
TEST_ATP_DEFAULTS_FILE = "scope3_methodology/test/defaults/atp-defaults.yaml"


class TestAPI(unittest.TestCase):
    """Test API startup and endpoints"""

    def test_startup(self):
        """Test api startup loads defaults correctly"""
        load_default_files(
            TEST_ATP_DEFAULTS_FILE,
            TEST_ORGANIZATION_DEFAULTS_FILE,
            TEST_PROPERTY_DEFAULTS_FILE,
            TEST_DEVICE_DEFAULTS_FILE,
        )

        # verify the correct count and a field that should be different across
        # all the different default types
        self.assertEqual(len(organization_defaults), 3)
        self.assertTrue(organization_defaults[OrganizationType.ATP])
        self.assertEqual(
            organization_defaults[
                OrganizationType.ATP
            ].travel_emissions_mt_co2e_per_employee_per_month,
            Decimal("0.01222221"),
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

    # TODO add in testing for API endpoints issue: #53


if __name__ == "__main__":
    unittest.main()
