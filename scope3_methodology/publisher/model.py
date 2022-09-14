""" Model for computing emissions for a publisher property """
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from utils.base_model import BaseModel
from utils.constants import MB_BYTES_PER_GB, SEC_PER_HOUR
from utils.utils import log_result, not_none


class EnvironmentIdleElectricityUseWattFields(Enum):
    """Idle electricity use watt fields per environment on property model"""

    COMPUTER = "computer_idle_electricity_use_watts"
    MOBILE = "mobile_idle_electricity_use_watts"
    TV = "tv_idle_electricity_use_watts"


class EnvironmentActiveElectricityUseWattFields(Enum):
    """Active electricity use watt fields per environment on property model"""

    COMPUTER = "computer_active_electricity_use_watts"
    MOBILE = "mobile_active_electricity_use_watts"
    TV = "tv_active_electricity_use_watts"


@dataclass
class ModeledProperty:
    """A modeled media property, representing a web site, mobile app, ctv channel, etc"""

    identifier: str
    impressions: float
    ad_revenue_allocation_pct: float
    data_transfer_electricity_kwh: float
    page_load_electricity_kwh: float
    client_device_emissions_g_co2e_per_imp: float
    corporate_emissions_g_co2e_per_impression: float | None

    def get_ad_revenue_allocation_rate(self):
        """Return the ad revenue allocation rate (decimal fraction)"""
        return self.ad_revenue_allocation_pct / 100.0

    def set_corporate_emissions_g_co2e_per_impression(
        self, emissions_g: float, emissions_g_per_imp: float
    ) -> None:
        """Compute and set the corporate emissions per impression in grams CO2e"""
        if emissions_g:
            self.corporate_emissions_g_co2e_per_impression = (
                emissions_g * self.get_ad_revenue_allocation_rate() / self.impressions
            )
        else:
            self.corporate_emissions_g_co2e_per_impression = emissions_g_per_imp
        log_result(
            f"{self.identifier} corporate emissions g co2e per impression",
            self.corporate_emissions_g_co2e_per_impression,
            1,
        )


@dataclass
class Property(BaseModel):
    """Raw emissions information about a property and methodology of how to calculate emissions"""

    environment: str = field(default="computer", metadata={"default_eligible": False})
    grid_intensity_g_co2e_per_kwh: float = field(default=539, metadata={"default_eligible": False})
    visits_per_month: Optional[float] = field(default=None, metadata={"default_eligible": False})
    average_visit_duration_s: Optional[float] = field(
        default=None, metadata={"default_eligible": False}
    )
    pages_per_visit: Optional[float] = field(default=None, metadata={"default_eligible": False})
    load_time_s: Optional[float] = field(default=None, metadata={"default_eligible": False})
    page_size_mb: Optional[float] = field(default=None, metadata={"default_eligible": False})
    quality_impressions_per_duration_s: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    revenue_allocation_to_digital_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    revenue_allocation_to_ads_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    computer_active_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    computer_idle_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    tv_active_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    tv_idle_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    mobile_active_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    mobile_idle_electricity_use_watts: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    servers_processing_bid_requests_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    end_user_data_transfer_electricity_use_kwh_per_gb: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    core_internet_data_transfer_electricity_use_kwh_per_gb: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    corporate_emissions_g_co2e_per_impression: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    defaults: Optional["Property"] = field(default=None, metadata={"default_eligible": False})

    def set_defaults(self, defaults: "Property"):
        """Set defaults to be used as fallback in computations"""
        self.defaults = defaults

    def get_revenue_allocation_to_digital_rate(self) -> float:
        """Return the revenue allocation to digitial rate (decimal fraction)"""
        return not_none(self.revenue_allocation_to_digital_pct) / 100.0

    def get_revenue_allocation_to_ads_rate(self) -> float:
        """Return the revenue allocation to ads rate (decimal fraction)"""
        return not_none(self.revenue_allocation_to_ads_pct) / 100.0

    def comp_ads_per_visit(self) -> float:
        """Compute the ads per visit"""
        return not_none(self.average_visit_duration_s) * not_none(
            self.quality_impressions_per_duration_s
        )

    def comp_impressions(self) -> float:
        """Compute the impressions for the property"""
        return not_none(self.visits_per_month) * not_none(self.comp_ads_per_visit())

    def comp_ad_revenue_allocation_pct(self) -> float:
        """Compute ad revenue allocation percentage"""
        return (
            self.get_revenue_allocation_to_digital_rate()
            * self.get_revenue_allocation_to_ads_rate()
        ) * 100

    def comp_active_page_load_time(self) -> float:
        """Compute active page load time"""
        return not_none(self.pages_per_visit) * not_none(self.load_time_s)

    def comp_browse_time(self) -> float:
        """Compute browse time"""
        return not_none(self.average_visit_duration_s) - self.comp_active_page_load_time()

    def get_environment_active_electricity_use_watts(self):
        """Return active electricity use in watts for property environment"""
        env_field = EnvironmentActiveElectricityUseWattFields[self.environment.upper()].value
        return self.__getattribute__(env_field)

    def get_environment_idle_electricity_use_watts(self):
        """Return idle electricity use in watts for property environment"""
        env_field = EnvironmentIdleElectricityUseWattFields[self.environment.upper()].value
        return self.__getattribute__(env_field)

    # get_energy_from_page_load
    def comp_energy_from_page_load_wh(
        self,
        depth: int,
    ) -> float:
        """Compute the energy from page load wh"""
        total_energy_wh = (
            self.comp_active_page_load_time() * self.get_environment_active_electricity_use_watts()
            + self.comp_browse_time() * self.get_environment_idle_electricity_use_watts()
        ) / SEC_PER_HOUR
        log_result("page load electricity wh", total_energy_wh, depth)

        # TODO - add embodied emissions factor here
        # https://circularcomputing.com/news/carbon-footprint-laptop/
        # https://pics.uvic.ca/sites/default/files/uploads/publications/Teehan,%20P.%20Article,%202013%20%202.pdf
        return total_energy_wh

    def comp_page_load_electricity_kwh(self, depth: int) -> float:
        """Compute the page load electricity kwh"""
        return self.comp_energy_from_page_load_wh(depth) / 1000 / self.comp_ads_per_visit()

    def comp_data_transfer_per_impression(self) -> float:
        """Compute the data transfer per impressions in mb per impression"""
        return not_none(self.page_size_mb) / self.comp_ads_per_visit()

    def comp_end_user_data_transfer_electricty_per_mb(self) -> float:
        """Compute the end user data transfer electricity per mb"""
        return not_none(self.end_user_data_transfer_electricity_use_kwh_per_gb) / MB_BYTES_PER_GB

    def comp_core_internet_data_transfer_electricty_per_mb(self) -> float:
        """Compute the core internet data transfer electricity per mb"""
        return (
            not_none(self.core_internet_data_transfer_electricity_use_kwh_per_gb) / MB_BYTES_PER_GB
        )

    def comp_electricity_per_mb(self) -> float:
        """Compute the electricity per mb used by tne end user and core internet data"""
        return (
            self.comp_end_user_data_transfer_electricty_per_mb()
            + self.comp_core_internet_data_transfer_electricty_per_mb()
        )

    def comp_data_transfer_electricity_kwh(self) -> float:
        """Compute the data transfer electricity in kwh"""
        return self.comp_electricity_per_mb() * self.comp_data_transfer_per_impression()

    def comp_client_device_emissions_g_co2e_per_impression(self, depth: int) -> float:
        """Compute the client device emissions per impressions in grams CO2e"""
        return self.grid_intensity_g_co2e_per_kwh * (
            self.comp_data_transfer_electricity_kwh() + self.comp_page_load_electricity_kwh(depth)
        )

    def model_property(self, identifier: str, defaults: "Property", depth: int) -> ModeledProperty:
        """ "
        Model a publisher property based on raw emissions data and constants.
        :return: ModeledProperty
        """
        self.set_defaults(defaults)

        # TODO - simulate auctions to multiple ad tech partners w/ cookie syncs
        impressions = self.comp_impressions()
        log_result("impressions per month", impressions, 2)

        ad_revenue_allocation_pct = self.comp_ad_revenue_allocation_pct()
        log_result("ad_revenue_allocation_pct", ad_revenue_allocation_pct, 2)

        page_load_electricity_kwh = self.comp_page_load_electricity_kwh(depth)
        log_result("page_load_electricity_kwh", page_load_electricity_kwh, 2)

        data_transfer_electricity_kwh = self.comp_data_transfer_electricity_kwh()
        log_result("data_transfer_electricity_kwh", data_transfer_electricity_kwh, 2)

        client_device_emissions_g_co2e_per_imp = (
            self.comp_client_device_emissions_g_co2e_per_impression(depth)
        )
        log_result(
            "client_device_emissions_g_co2e_per_impression",
            client_device_emissions_g_co2e_per_imp,
            2,
        )

        return ModeledProperty(
            identifier,
            impressions,
            ad_revenue_allocation_pct,
            data_transfer_electricity_kwh,
            page_load_electricity_kwh,
            client_device_emissions_g_co2e_per_imp,
            self.corporate_emissions_g_co2e_per_impression,
        )
