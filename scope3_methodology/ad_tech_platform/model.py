""" Model for computing emissions for an ad tech platform"""
from dataclasses import dataclass, field
from typing import Optional

from utils.base_model import BaseModel
from utils.constants import BILLION, BYTES_PER_GB, G_PER_MT
from utils.utils import log_result, not_none


@dataclass
class ModeledAdTechPlatform:
    """This represents a modeled node in our graph"""

    name: str
    identifier: str
    primary_bid_request_emissions_g_co2e: float
    primary_cookie_sync_emissions_g_co2e: float
    corporate_emissions_g_co2e_per_bid_request: float | None = None
    cookie_sync_distribution_ratio: float | None = None
    atp_block_rate: float = 0.0
    secondary_bid_request_emissions_g_co2e: float | None = None
    secondary_cookie_sync_emissions_g_co2e: float | None = None


@dataclass
class DistributionPartner:
    """This represents an edge in our graph"""

    partner: ModeledAdTechPlatform
    bid_request_distribution_rate: float


@dataclass
class AdTechPlatform(BaseModel):
    """Raw emissions information about an ATP and methodology of how to calculate emissions"""

    allocation_of_company_servers_pct: Optional[float] = field(
        default=100, metadata={"default_eligible": False}
    )
    allocation_of_corporate_emissions_pct: Optional[float] = field(
        default=100, metadata={"default_eligible": False}
    )
    corporate_emissions_g_co2e_per_bid_request: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_requests_processed_from_ad_tech_platforms_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_request_size_in_bytes: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_to_server_emissions_g_co2e_per_gb: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_emissions_mt_co2e_per_month: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    servers_processing_bid_requests_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    atp_block_rate: Optional[float] = field(default=None, metadata={"default_eligible": True})
    cookie_syncs_processed_per_bid_request: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    datacenter_water_intensity_h2o_m_3_per_mwh: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    server_emissions_g_co2e_per_kwh: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    servers_processing_cookie_syncs_pct: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    cookie_sync_distribution_ratio: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    bid_requests_processed_billion_per_month: Optional[float] = field(
        default=None, metadata={"default_eligible": True}
    )
    ad_tech_platform_bid_requests_processed_billion_per_month: Optional[float] = field(
        default=None, metadata={"default_eligible": False}
    )
    cookie_syncs_processed_billion_per_month: Optional[float] = field(
        default=None, metadata={"default_eligible": False}
    )
    data_transfer_emissions_mt_co2e_per_month: Optional[float] = field(
        default=None, metadata={"default_eligible": False}
    )
    defaults: Optional["AdTechPlatform"] = field(default=None, metadata={"default_eligible": False})

    def set_defaults(self, defaults: "AdTechPlatform"):
        """Set defaults to be used as fallback in computations"""
        self.defaults = defaults

    def get_bid_requests_processed_per_month(self) -> float:
        """Returns bif requests total processed per month"""
        return not_none(self.bid_requests_processed_billion_per_month) * BILLION

    def get_server_emissions_g_co2e_per_month(self) -> float:
        """Returns server emissions per month in grams"""
        return not_none(self.server_emissions_mt_co2e_per_month) * G_PER_MT

    def get_cookie_syncs_processed_per_month(self) -> float | None:
        """Returns cookies syncs processed per month"""
        if self.cookie_syncs_processed_billion_per_month:
            return self.cookie_syncs_processed_billion_per_month * BILLION
        return None

    def get_servers_processing_bid_requests_rate(self) -> float:
        """Returns servers processing bid requests rate (decimal fraction)"""
        return not_none(self.servers_processing_bid_requests_pct) / 100.0

    def get_servers_processing_cookie_syncs_rate(self) -> float:
        """Returns servers processing cookie syncs rate (decimal fraction)"""
        return not_none(self.servers_processing_cookie_syncs_pct) / 100.0

    def get_allocation_of_corporate_emissions_rate(self) -> float:
        """Returns allocation of corporate emissions rate (decimal fraction)"""
        return not_none(self.allocation_of_corporate_emissions_pct) / 100.0

    def get_bid_requests_processed_from_ad_tech_platforms_rate(self) -> float:
        """Returns bid requests processed from incoming ATPs rate (decimal fraction)"""
        return not_none(self.bid_requests_processed_from_ad_tech_platforms_pct) / 100.0

    def get_data_transfer_emissions_g_co2e_per_month(self) -> float | None:
        """Returns data transfere emissions per month in grams"""
        if self.data_transfer_emissions_mt_co2e_per_month:
            return self.data_transfer_emissions_mt_co2e_per_month * G_PER_MT
        return None

    def get_allocation_of_company_servers_rate(self) -> float:
        """Returns allocation of company servers rate (decimal fraction)"""
        return not_none(self.allocation_of_company_servers_pct) / 100.0

    def comp_external_request_rate(self, depth: int) -> float:
        """
        Compute the external request rate.

        We assume that server-to-server requests (generally from ad tech platforms) incur core
        networking costs that are not accounted for in client device data transfer emissions.
        Therefore we need to figure out what portion of inbound requests are S2S.
        """
        if (
            self.ad_tech_platform_bid_requests_processed_billion_per_month
            and self.bid_requests_processed_billion_per_month
        ):
            rate = (
                self.ad_tech_platform_bid_requests_processed_billion_per_month
                / self.bid_requests_processed_billion_per_month
            )
            log_result("external request rate", f"{rate}%", depth)
            return rate
        return self.get_bid_requests_processed_from_ad_tech_platforms_rate()

    def comp_bid_request_size_gb(self) -> float:
        """Compute the bid requests size in GB"""
        return not_none(self.bid_request_size_in_bytes) / BYTES_PER_GB

    def comp_data_transfer_emissions_g_co2e_per_bid_request(self, depth: int) -> float:
        """Compute the data transfer emissions per bid request in grams CO2e"""
        data_transfer_emissions_g_co2e_per_month = (
            self.get_data_transfer_emissions_g_co2e_per_month()
        )
        if data_transfer_emissions_g_co2e_per_month:
            return data_transfer_emissions_g_co2e_per_month

        data_transfer_emissions_g_co2e_per_bid_request = (
            self.comp_external_request_rate(depth - 1)
            * self.comp_bid_request_size_gb()
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
    ) -> float:
        """Compute the server emissions per bid request in grams CO2e"""
        server_emissions_g_co2e_per_bid_request = (
            self.get_allocation_of_company_servers_rate()
            * self.get_server_emissions_g_co2e_per_month()
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
    ) -> float:
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
    ) -> float:
        """
        Compute the secondary emissions from distribution partners per bid request
        in grams CO2e.
        """
        secondary_emissions_per_bid_request = 0.0
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

    def comp_cookie_syncs_processed_per_month(self, depth: int) -> float:
        """Compute the total number of cookies syncs processed per month"""
        cookie_syncs_processed_per_month = self.get_cookie_syncs_processed_per_month()
        if cookie_syncs_processed_per_month:
            return cookie_syncs_processed_per_month

        cookie_syncs_processed = self.get_bid_requests_processed_per_month() * not_none(
            self.cookie_syncs_processed_per_bid_request
        )
        log_result("cookie syncs processed per month", cookie_syncs_processed, depth)
        return cookie_syncs_processed

    def comp_water_usage_to_emissions_ratio_h2o_m_3_per_g_co2e(self, depth: int) -> float:
        """Compute the water usage to emissions rate (H2O m^3 per gCO2e)"""
        water_m3_per_emissions = (
            not_none(self.datacenter_water_intensity_h2o_m_3_per_mwh)
            / not_none(self.server_emissions_g_co2e_per_kwh)
            / 1000
        )
        log_result("h2o m^3 per g co2e emissions", water_m3_per_emissions, depth)
        return water_m3_per_emissions

    def comp_primary_emissions_g_co2e_per_cookie_sync(
        self,
        depth: int,
    ) -> float:
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
    ) -> float:
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
    ) -> float:
        """
        Compute the secondary emissions from distribution partners per cookie sync
        in grams CO2e.
        """
        secondary_emissions_per_cookie_sync = 0.0
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
        corporate_emissions_g: Optional[float] = None,
        corporate_emissions_g_per_bid_request: Optional[float] = None,
    ) -> float:
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
        corporate_emissions_g: float | None = None,
        corporate_emissions_g_per_bid_request: float | None = None,
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
            # TODO once cookie sync logic is updated uncomment this code
            # secondary_emissions_per_cookie_sync = (
            #     self.comp_secondary_emissions_g_co2e_per_cookie_sync(distribution_partners, depth)
            # )

        return ModeledAdTechPlatform(
            name,
            identifier,
            primary_emissions_per_bid_request,
            primary_emissions_per_cookie_sync,
            self.corporate_emissions_g_co2e_per_bid_request,
            self.cookie_sync_distribution_ratio,
            not_none(self.atp_block_rate),
            secondary_emissions_per_bid_request,
            secondary_emissions_per_cookie_sync,
        )
