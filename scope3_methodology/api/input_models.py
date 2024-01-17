""" API Input Models """
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from scope3_methodology.ad_tech_platform.model import DistributionPartner


class StreamingResolution(Enum):
    """Networking Connection Types"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class NetworkingConnectionType(Enum):
    """Networking Connection Types"""

    FIXED = "fixed"
    MOBILE = "mobile"
    UNKNOWN = "unknown"


class ATPTemplate(Enum):
    """ATP Template Types"""

    DSP = "dsp"
    SSP = "ssp"


class PropertyChannel(Enum):
    """Property Template Types"""

    DISPLAY = "display"
    DISPLAY_APP = "display-web"
    DISPLAY_WEB = "display-app"
    STREAMING = "streaming"
    STREAMING_VIDEO = "streaming-video"
    SOCIAL = "social"
    DIGITAL_AUDIO = "digital-audio"
    CTV_BVOD = "ctv-bvod"


class EndUserDevices(Enum):
    """End user devices"""

    PERSONAL_COMPUTER = "personal_computer"
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    TV_SYSTEM = "tv_system"
    SMART_SPEAKER = "smart_speaker"


class OrganizationType(Enum):
    """Organization Types"""

    GENERIC = "generic"
    PUBLISHER = "publisher"
    ATP = "atp"


class CorporateInput(BaseModel):
    """/calculate/corporate input"""

    org_type: OrganizationType
    number_of_employees: Optional[int]
    office_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = None
    datacenter_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = None
    travel_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = None
    commuting_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = None
    overhead_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = None
    corporate_emissions_mt_co2e_per_month: Optional[Decimal] = None
    revenue_allocation_to_digital_ads_pct: Optional[Decimal] = None


class ATPInput(BaseModel):
    """/calculate/atp input"""

    name: str = ""
    identifier: str = ""
    atp_template: ATPTemplate
    corporate_emissions_g_co2e: Optional[Decimal] = None
    allocation_of_company_servers_pct: Optional[Decimal] = None
    allocation_of_corporate_emissions_pct: Optional[Decimal] = None
    corporate_emissions_g_co2e_per_bid_request: Optional[Decimal] = None
    bid_requests_processed_from_publishers_pct: Optional[Decimal] = None
    bid_requests_processed_from_ad_tech_platforms_pct: Optional[Decimal] = None
    bid_request_size_in_bytes: Optional[Decimal] = None
    server_to_server_emissions_g_co2e_per_gb: Optional[Decimal] = None
    server_emissions_mt_co2e_per_month: Optional[Decimal] = None
    servers_processing_bid_requests_pct: Optional[Decimal] = None
    cookie_syncs_processed_per_bid_request: Optional[Decimal] = None
    datacenter_water_intensity_h2o_m_3_per_mwh: Optional[Decimal] = None
    server_emissions_g_co2e_per_kwh: Optional[Decimal] = None
    servers_processing_cookie_syncs_pct: Optional[Decimal] = None
    cookie_sync_distribution_ratio: Optional[Decimal] = None
    bid_requests_processed_billion_per_month: Optional[Decimal] = None
    cookie_syncs_processed_billion_per_month: Optional[Decimal] = None
    data_transfer_emissions_mt_co2e_per_month: Optional[Decimal] = None


class ATPSecondaryEmissionsInput(BaseModel):
    """/calculate/atp_secondary_bid_request_emissions input"""

    partners: list[DistributionPartner]
