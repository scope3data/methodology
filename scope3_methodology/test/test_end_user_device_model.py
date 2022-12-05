""" Tests for compute emissions for a end user device emissions """
import unittest
from decimal import Decimal

from scope3_methodology.end_user_device.model import EndUserDevice, ModeledEndUserDevice

TEST_DEVICE = "personal_computer"
TEST_CHANNEL = "display"
TEST_TEMPLATE = "generic"
TEST_DEFAULTS_FILE = "defaults/end_user_device-defaults.yaml"
TEST_QUALITY_IMPRESSIONS_PER_SEC = Decimal("0.1")


class TestEndUserDeviceModel(unittest.TestCase):
    """Test EndUserDeviceModel functions"""

    def test_load_defaults(self):
        """Test load defaults"""
        device = EndUserDevice.load_default_yaml(TEST_DEVICE, TEST_DEFAULTS_FILE)
        self.assertEqual(device.draw_watts, Decimal("53.200000000"))
        self.assertEqual(device.production_emissions_gco2e_per_duration_s, Decimal("0.007000000"))

    def test_load_defaults_invalid_device(self):
        """Test load defaults"""
        with self.assertRaises(Exception):
            EndUserDevice.load_default_yaml("unknown_device", TEST_DEFAULTS_FILE)

    def test_compute_production_emissions_gco2e_per_imp(self):
        """Test compute production emissions"""
        device = EndUserDevice.load_default_yaml(TEST_DEVICE, TEST_DEFAULTS_FILE)
        production_gco2e_per_imp = device.compute_production_emissions_gco2e_per_imp(
            TEST_QUALITY_IMPRESSIONS_PER_SEC
        )
        self.assertEqual(production_gco2e_per_imp, Decimal("0.07000000"))

    def test_compute_power_emissions_kwh_per_imp(self):
        """Test compute power emissions"""
        device = EndUserDevice.load_default_yaml(TEST_DEVICE, TEST_DEFAULTS_FILE)
        power_kwh_per_imp = device.compute_power_emissions_kwh_per_imp(
            TEST_QUALITY_IMPRESSIONS_PER_SEC
        )
        self.assertEqual(power_kwh_per_imp, Decimal("0.0001477777777777777777777777778"))

    def test_model_end_user_device_personal_computer(self):
        """Test model end user devices"""
        device = EndUserDevice.load_default_yaml(TEST_DEVICE, TEST_DEFAULTS_FILE)
        modeled_d = device.model_end_user_device(
            TEST_DEVICE, TEST_CHANNEL, TEST_TEMPLATE, TEST_QUALITY_IMPRESSIONS_PER_SEC
        )
        self.assertEqual(
            modeled_d,
            ModeledEndUserDevice(
                TEST_DEVICE,
                TEST_CHANNEL,
                TEST_TEMPLATE,
                Decimal("0.0001477777777777777777777777778"),
                Decimal("0.07000000"),
            ),
        )

    def test_model_end_user_device_smartphone(self):
        """Test model end user devices"""
        smartphone = "smartphone"
        device = EndUserDevice.load_default_yaml(smartphone, TEST_DEFAULTS_FILE)
        modeled_d = device.model_end_user_device(
            smartphone, TEST_CHANNEL, TEST_TEMPLATE, TEST_QUALITY_IMPRESSIONS_PER_SEC
        )
        self.assertEqual(
            modeled_d,
            ModeledEndUserDevice(
                smartphone,
                TEST_CHANNEL,
                TEST_TEMPLATE,
                Decimal("0.000002138888888888888888888888889"),
                Decimal("0.052000000"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
