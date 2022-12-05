""" API Input Models """
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from scope3_methodology.ad_tech_platform.model import DistributionPartner


class ATPTemplate(Enum):
    """ATP Template Types"""

    DSP = "dsp"
    SSP = "ssp"


class PropertyChannel(Enum):
    """Property Template Types"""

    DISPLAY = "display"
    STREAMING = "streaming"


class EndUserDevices(Enum):
    """End user devices"""

    PERSONAL_COMPUTER = "personal_computer"
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    TV_SYSTEM = "tv_system"


class OrganizationType(Enum):
    """Organization Types"""

    GENERIC = "generic"
    PUBLISHER = "publisher"
    ATP = "atp"


class CorporateInput(BaseModel):
    """/calculate/corporate input"""

    org_type: OrganizationType
    number_of_employees: Optional[int]
    office_emissions_mt_co2e_per_employee_per_month: Optional[Decimal]
    datacenter_emissions_mt_co2e_per_employee_per_month: Optional[Decimal]
    travel_emissions_mt_co2e_per_employee_per_month: Optional[Decimal]
    commuting_emissions_mt_co2e_per_employee_per_month: Optional[Decimal]
    overhead_emissions_mt_co2e_per_employee_per_month: Optional[Decimal]
    corporate_emissions_mt_co2e_per_month: Optional[Decimal]


class ATPInput(BaseModel):
    """/calculate/atp input"""

    name: str = ""
    identifier: str = ""
    atp_template: ATPTemplate
    corporate_emissions_g_co2e: Optional[Decimal]
    allocation_of_company_servers_pct: Optional[Decimal]
    allocation_of_corporate_emissions_pct: Optional[Decimal]
    corporate_emissions_g_co2e_per_bid_request: Optional[Decimal]
    bid_requests_processed_from_publishers_pct: Optional[Decimal]
    bid_requests_processed_from_ad_tech_platforms_pct: Optional[Decimal]
    bid_request_size_in_bytes: Optional[Decimal]
    server_to_server_emissions_g_co2e_per_gb: Optional[Decimal]
    server_emissions_mt_co2e_per_month: Optional[Decimal]
    servers_processing_bid_requests_pct: Optional[Decimal]
    cookie_syncs_processed_per_bid_request: Optional[Decimal]
    datacenter_water_intensity_h2o_m_3_per_mwh: Optional[Decimal]
    server_emissions_g_co2e_per_kwh: Optional[Decimal]
    servers_processing_cookie_syncs_pct: Optional[Decimal]
    cookie_sync_distribution_ratio: Optional[Decimal]
    bid_requests_processed_billion_per_month: Optional[Decimal]
    cookie_syncs_processed_billion_per_month: Optional[Decimal]
    data_transfer_emissions_mt_co2e_per_month: Optional[Decimal]


class ATPSecondaryEmissionsInput(BaseModel):
    """/calculate/atp_secondary_bid_request_emissions input"""

    partners: list[DistributionPartner]
