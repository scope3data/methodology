""" Model for computing emissions for an ad tech platform"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from scope3_methodology.utils.constants import (
    BILLION,
    BYTES_PER_GB,
    G_PER_MT,
    ONE_HUNDRED,
)
from scope3_methodology.utils.custom_base_model import CustomBaseModel
from scope3_methodology.utils.utils import log_result, not_none


@dataclass
class ModeledAdTechPlatform:
    """This represents a modeled node in our graph"""

    name: str
    identifier: str
    primary_bid_request_emissions_g_co2e: Decimal
    primary_cookie_sync_emissions_g_co2e: Decimal
    corporate_emissions_g_co2e_per_bid_request: Decimal | None = None
    cookie_sync_distribution_ratio: Decimal | None = None
    atp_block_rate: Decimal = Decimal("0.0")
    publisher_block_rate: Decimal = Decimal("0.0")
    secondary_bid_request_emissions_g_co2e: Decimal | None = None
    secondary_cookie_sync_emissions_g_co2e: Decimal | None = None


@dataclass
class DistributionPartner:
    """This represents an edge in our graph"""

    partner: ModeledAdTechPlatform
    bid_request_distribution_rate: Decimal


@dataclass
class AdTechPlatform(CustomBaseModel):
    """Raw emissions information about an ATP and methodology of how to calculate emissions"""

    allocation_of_company_servers_pct: Optional[Decimal] = field(
        default=ONE_HUNDRED, metadata={"default_eligible": False}
    )
    allocation_of_corporate_emissions_pct: Optional[Decimal] = field(
        default=ONE_HUNDRED, metadata={"default_eligible": False}
    )
    corporate_emissions_g_co2e_per_bid_request: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_requests_processed_from_ad_tech_platforms_pct: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_requests_processed_from_publishers_pct: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_request_size_in_bytes: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    depreciation_dollars_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": False}
    )
    server_emissions_mt_per_dollar_of_depreciation: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_to_server_emissions_g_co2e_per_gb: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_emissions_mt_co2e_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    servers_processing_bid_requests_pct: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    cookie_syncs_processed_per_bid_request: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    datacenter_water_intensity_h2o_m_3_per_mwh: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_emissions_g_co2e_per_kwh: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    servers_processing_cookie_syncs_pct: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    cookie_sync_distribution_ratio: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_requests_processed_billion_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    cookie_syncs_processed_billion_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": False}
    )
    data_transfer_emissions_mt_co2e_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": False}
    )
    defaults: Optional["AdTechPlatform"] = field(default=None, metadata={"default_eligible": False})

    def set_defaults(self, defaults: "AdTechPlatform"):
        """Set defaults to be used as fallback in computations"""
        self.defaults = defaults

    def get_bid_requests_processed_per_month(self) -> Decimal:
        """Returns bid requests total processed per month"""
        return not_none(self.bid_requests_processed_billion_per_month) * BILLION

    def get_server_emissions_g_co2e_per_month(self) -> Decimal:
        """Returns server emissions per month in grams"""
        if self.depreciation_dollars_per_month:
            return (
                not_none(self.server_emissions_mt_per_dollar_of_depreciation)
                * self.depreciation_dollars_per_month
                * G_PER_MT
            )
        return not_none(self.server_emissions_mt_co2e_per_month) * G_PER_MT

    def get_cookie_syncs_processed_per_month(self) -> Decimal | None:
        """Returns cookies syncs processed per month"""
        if self.cookie_syncs_processed_billion_per_month:
            return self.cookie_syncs_processed_billion_per_month * BILLION
        return None

    def get_servers_processing_bid_requests_rate(self) -> Decimal:
        """Returns servers processing bid requests rate (decimal fraction)"""
        return not_none(self.servers_processing_bid_requests_pct) / ONE_HUNDRED

    def get_servers_processing_cookie_syncs_rate(self) -> Decimal:
        """Returns servers processing cookie syncs rate (decimal fraction)"""
        return not_none(self.servers_processing_cookie_syncs_pct) / ONE_HUNDRED

    def get_allocation_of_corporate_emissions_rate(self) -> Decimal:
        """Returns allocation of corporate emissions rate (decimal fraction)"""
        return not_none(self.allocation_of_corporate_emissions_pct) / ONE_HUNDRED

    def get_bid_requests_processed_from_ad_tech_platforms_rate(self) -> Decimal:
        """Returns bid requests processed from incoming ATPs rate (decimal fraction)"""

        return not_none(self.bid_requests_processed_from_ad_tech_platforms_pct) / ONE_HUNDRED

    def get_bid_requests_processed_from_publishers_rate(self) -> Decimal:
        """Returns bid requests processed from incoming Publishers rate (decimal fraction)"""
        return not_none(self.bid_requests_processed_from_publishers_pct) / ONE_HUNDRED

    def get_data_transfer_emissions_g_co2e_per_month(self) -> Decimal | None:
        """Returns data transfere emissions per month in grams"""
        if self.data_transfer_emissions_mt_co2e_per_month:
            return self.data_transfer_emissions_mt_co2e_per_month * G_PER_MT
        return None

    def get_allocation_of_company_servers_rate(self) -> Decimal:
        """Returns allocation of company servers rate (decimal fraction)"""
        return not_none(self.allocation_of_company_servers_pct) / ONE_HUNDRED

    def get_atp_block_rate(self) -> Decimal:
        """
        Returns the computed block rate, or requests blocked from incoming bid requests
        from adtech platforms
        """
        return 1 - self.get_bid_requests_processed_from_ad_tech_platforms_rate()

    def get_publisher_block_rate(self) -> Decimal:
        """
        Returns the computed block rate, or requests blocked from incoming direct bid
        requests from publishers
        """
        return 1 - self.get_bid_requests_processed_from_publishers_rate()

    def comp_bid_request_size_gb(self) -> Decimal:
        """Compute the bid requests size in GB"""
        return not_none(self.bid_request_size_in_bytes) / BYTES_PER_GB

    def comp_data_transfer_emissions_g_co2e_per_bid_request(self, depth: int) -> Decimal:
        """Compute the data transfer emissions per bid request in grams CO2e"""
        data_transfer_emissions_g_co2e_per_month = (
            self.get_data_transfer_emissions_g_co2e_per_month()
        )
        if data_transfer_emissions_g_co2e_per_month:
            return data_transfer_emissions_g_co2e_per_month

        data_transfer_emissions_g_co2e_per_bid_request = (
            self.comp_bid_request_size_gb()
            * not_none(self.server_to_server_emissions_g_co2e_per_gb)
        ) / self.get_bid_requests_processed_per_month()
        log_result(
            "data transfer emissions g co2e per bid request",
            f"{data_transfer_emissions_g_co2e_per_bid_request:.8f}",
            depth,
        )
        return data_transfer_emissions_g_co2e_per_bid_request

    def comp_server_emissions_g_co2e_per_bid_request(
        self,
        depth: int,
    ) -> Decimal:
        """Compute the server emissions per bid request in grams CO2e"""
        server_emissions_g = self.get_server_emissions_g_co2e_per_month()
        log_result(
            "server emissions g co2e per month",
            f"{server_emissions_g:.6f}",
            depth - 1,
        )
        server_emissions_g_co2e_per_bid_request = (
            self.get_allocation_of_company_servers_rate()
            * server_emissions_g
            * self.get_servers_processing_bid_requests_rate()
        ) / self.get_bid_requests_processed_per_month()

        log_result(
            "server emissions g co2e per bid request",
            f"{server_emissions_g_co2e_per_bid_request:.6f}",
            depth,
        )
        return server_emissions_g_co2e_per_bid_request

    def comp_primary_emissions_g_co2e_per_bid_request(
        self,
        depth: int,
    ) -> Decimal:
        """Compute the primary emissions per bid request in grams CO2e"""
        data_transfer_emissions_g_co2e_per_bid_request = (
            self.comp_data_transfer_emissions_g_co2e_per_bid_request(depth - 1)
        )

        server_emissions_g_co2e_per_bid_request = self.comp_server_emissions_g_co2e_per_bid_request(
            depth - 1
        )
        primary_emissions_g_co2e_per_bid_request = (
            not_none(self.corporate_emissions_g_co2e_per_bid_request)
            + not_none(data_transfer_emissions_g_co2e_per_bid_request)
            + server_emissions_g_co2e_per_bid_request
        )
        log_result(
            "primary emissions g co2e per bid request",
            f"{primary_emissions_g_co2e_per_bid_request:.6f}",
            depth,
        )
        return primary_emissions_g_co2e_per_bid_request

    def comp_secondary_emissions_g_co2e_per_bid_request(
        self, distribution_partners: list[DistributionPartner], depth: int
    ) -> Decimal:
        """
        Compute the secondary emissions from distribution partners per bid request
        in grams CO2e.
        """
        secondary_emissions_per_bid_request = Decimal("0.0")
        if distribution_partners:
            for edge in distribution_partners:
                dp_emissions = (
                    1 - edge.partner.atp_block_rate
                ) * edge.partner.primary_bid_request_emissions_g_co2e
                secondary_emissions_per_bid_request += (
                    edge.bid_request_distribution_rate * dp_emissions
                )
            log_result(
                "secondary emissions g co2e per bid request",
                secondary_emissions_per_bid_request,
                depth,
            )
        return secondary_emissions_per_bid_request

    def comp_cookie_syncs_processed_per_month(self, depth: int) -> Decimal:
        """Compute the total number of cookies syncs processed per month"""
        cookie_syncs_processed_per_month = self.get_cookie_syncs_processed_per_month()
        if cookie_syncs_processed_per_month:
            return cookie_syncs_processed_per_month

        cookie_syncs_processed = self.get_bid_requests_processed_per_month() * not_none(
            self.cookie_syncs_processed_per_bid_request
        )
        log_result("cookie syncs processed per month", cookie_syncs_processed, depth)
        return cookie_syncs_processed

    def comp_water_usage_to_emissions_ratio_h2o_m_3_per_g_co2e(self, depth: int) -> Decimal:
        """Compute the water usage to emissions rate (H2O m^3 per gCO2e)"""
        water_m3_per_emissions = (
            not_none(self.datacenter_water_intensity_h2o_m_3_per_mwh)
            / not_none(self.server_emissions_g_co2e_per_kwh)
            / Decimal("1000.0")
        )
        log_result("h2o m^3 per g co2e emissions", water_m3_per_emissions, depth)
        return water_m3_per_emissions

    def comp_primary_emissions_g_co2e_per_cookie_sync(
        self,
        depth: int,
    ) -> Decimal:
        """Compute the primary emissions per cookie sync in grams CO2e"""
        primary_emissions_per_cookie_sync = (
            self.get_allocation_of_company_servers_rate()
            * self.get_server_emissions_g_co2e_per_month()
            * self.get_servers_processing_cookie_syncs_rate()
        ) / self.comp_cookie_syncs_processed_per_month(depth)

        log_result("primary emissions g per cookie sync", primary_emissions_per_cookie_sync, depth)
        return primary_emissions_per_cookie_sync

    def comp_water_usage_per_cookie_sync(
        self,
        depth: int,
    ) -> Decimal:
        """Compute the water usuage per cookie sync"""
        water_usage_to_emissions_ratio = (
            self.comp_water_usage_to_emissions_ratio_h2o_m_3_per_g_co2e(depth - 1)
        )
        primary_water_usage = (
            self.comp_primary_emissions_g_co2e_per_cookie_sync(depth)
            * water_usage_to_emissions_ratio
        )
        log_result("primary water usage m^3 per cookie sync", primary_water_usage, depth)
        return primary_water_usage

    def comp_secondary_emissions_g_co2e_per_cookie_sync(
        self, distribution_partners: list[DistributionPartner], depth: int
    ) -> Decimal:
        """
        Compute the secondary emissions from distribution partners per cookie sync
        in grams CO2e.
        """
        secondary_emissions_per_cookie_sync = Decimal("0.0")
        if distribution_partners:
            for edge in distribution_partners:
                secondary_emissions_per_cookie_sync += (
                    edge.partner.primary_cookie_sync_emissions_g_co2e
                )
            secondary_emissions_per_cookie_sync *= not_none(self.cookie_sync_distribution_ratio)
            log_result(
                "secondary emissions g per cookie sync",
                f"{secondary_emissions_per_cookie_sync:.6f}",
                depth,
            )
        return secondary_emissions_per_cookie_sync

    def comp_corporate_emissions_g_co2e_per_bid_request(
        self,
        defaults: "AdTechPlatform",
        corporate_emissions_g: Optional[Decimal] = None,
        corporate_emissions_g_per_bid_request: Optional[Decimal] = None,
    ) -> Decimal:
        """Compute the corporate emissions per bid request in grams CO2e"""
        corporate_emissions_g_co2e_per_bid_request = (
            defaults.corporate_emissions_g_co2e_per_bid_request
        )
        if corporate_emissions_g_per_bid_request or corporate_emissions_g:
            corporate_emissions_g_co2e_per_bid_request = corporate_emissions_g_per_bid_request
            if corporate_emissions_g:
                corporate_emissions_g_co2e_per_bid_request = (
                    self.get_allocation_of_corporate_emissions_rate()
                    * corporate_emissions_g
                    / self.get_bid_requests_processed_per_month()
                )
                log_result(
                    "corporate emissions g co2e per bid request",
                    f"{corporate_emissions_g_co2e_per_bid_request}:.8f",
                    1,
                )

        if not corporate_emissions_g_co2e_per_bid_request:
            raise Exception("failed to compute corporate emissions per bid request")
        self.corporate_emissions_g_co2e_per_bid_request = corporate_emissions_g_co2e_per_bid_request
        return corporate_emissions_g_co2e_per_bid_request

    def model_product(
        self,
        name: str,
        identifier: str,
        defaults: "AdTechPlatform",
        distribution_partners: list[DistributionPartner],
        corporate_emissions_g: Decimal | None = None,
        corporate_emissions_g_per_bid_request: Decimal | None = None,
        depth: int = 1,
    ) -> ModeledAdTechPlatform:
        """
        Model a product adtech platform) based on raw emissions data and constants.
        :return: ModeledAdTechPlatform
        """
        # Set defaults for all functions to use for fallback during comp
        self.set_defaults(defaults)

        # Compute corporate emissions
        self.comp_corporate_emissions_g_co2e_per_bid_request(
            defaults, corporate_emissions_g, corporate_emissions_g_per_bid_request
        )

        # Compute emissions
        primary_emissions_per_bid_request = self.comp_primary_emissions_g_co2e_per_bid_request(
            depth
        )
        primary_emissions_per_cookie_sync = self.comp_primary_emissions_g_co2e_per_cookie_sync(
            depth
        )

        secondary_emissions_per_bid_request = None
        secondary_emissions_per_cookie_sync = None
        if len(distribution_partners) > 0:
            secondary_emissions_per_bid_request = (
                self.comp_secondary_emissions_g_co2e_per_bid_request(distribution_partners, depth)
            )
            secondary_emissions_per_cookie_sync = (
                self.comp_secondary_emissions_g_co2e_per_cookie_sync(distribution_partners, depth)
            )

        return ModeledAdTechPlatform(
            name,
            identifier,
            primary_emissions_per_bid_request,
            primary_emissions_per_cookie_sync,
            self.corporate_emissions_g_co2e_per_bid_request,
            self.cookie_sync_distribution_ratio,
            self.get_atp_block_rate(),
            self.get_publisher_block_rate(),
            secondary_emissions_per_bid_request,
            secondary_emissions_per_cookie_sync,
        )
