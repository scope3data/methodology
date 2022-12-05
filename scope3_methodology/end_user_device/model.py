""" Model for computing emissions for the end user devices """

from dataclasses import dataclass, field
from decimal import Decimal

from scope3_methodology.utils.custom_base_model import CustomBaseModel
from scope3_methodology.utils.utils import log_result


@dataclass
class ModeledEndUserDevice:
    """A modeled end user device"""

    device: str
    channel: str
    template: str
    power_kwh_per_imp: Decimal
    production_gco2e_per_imp: Decimal


@dataclass
class EndUserDevice(CustomBaseModel):
    """
    Raw emissions information about an end-user device and methodology of
    how to calculate emissions for a specific property channel and template
    """

    production_emissions_gco2e_per_duration_s: Decimal = field(metadata={"default_eligible": True})
    draw_watts: Decimal = field(metadata={"default_eligible": True})

    def compute_production_emissions_gco2e_per_imp(self, quality_ads_per_second: Decimal):
        """Compute the production emissiions in gCO2e per impression"""
        gco2e_per_imp = (1 / quality_ads_per_second) * (
            self.production_emissions_gco2e_per_duration_s
        )
        log_result("production_emissions_gco2e_per_imp", gco2e_per_imp, 2)
        return gco2e_per_imp

    def compute_power_emissions_kwh_per_imp(self, quality_ads_per_second: Decimal):
        """Compute the power emissiions in kilowatt hours per impression"""
        ws_per_imp = (1 / quality_ads_per_second) * (self.draw_watts)
        kwh_per_imp = ws_per_imp / Decimal("3600") / Decimal("1000")
        log_result("power_emissions_kwh_per_imp", kwh_per_imp, 2)
        return kwh_per_imp

    def model_end_user_device(
        self,
        device: str,
        channel: str,
        template: str,
        quality_impressions_per_duration_s: Decimal,
    ) -> ModeledEndUserDevice | None:
        """
        Model an end user device based on raw emissions data and constants.
        :return: ModeledEndUserDevice
        """
        # Compute Emissions
        power_kwh_per_imp = self.compute_power_emissions_kwh_per_imp(
            quality_impressions_per_duration_s
        )
        production_gco2e_per_imp = self.compute_production_emissions_gco2e_per_imp(
            quality_impressions_per_duration_s
        )

        return ModeledEndUserDevice(
            device,
            channel,
            template,
            power_kwh_per_imp,
            production_gco2e_per_imp,
        )
