import os
from enum import Enum
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from pydantic import BaseModel

from scope3_methodology.ad_tech_platform.model import (
    AdTechPlatform,
    DistributionPartner,
)
from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.publisher.model import Property

app = FastAPI()


@app.route("/")
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


class ATPTemplate(Enum):
    DSP = "dsp"
    SSP = "ssp"
    NETWORK = "network"


class PropertyTemplate(Enum):
    NEWS_WITH_PRINT = "news_with_print"


class OrganizationType(Enum):
    GENERIC = "generic"
    PUBLISHER = "publisher"
    ATP = "atp"


organization_defaults: dict[OrganizationType, CorporateEmissions] = {}
adtech_platform_defaults: dict[ATPTemplate, AdTechPlatform] = {}
property_defaults: dict[PropertyTemplate, Property] = {}
atp_defaults_file_path = os.environ.get("ATP_DEFAULTS_FILE")
organization_defaults_file_path = os.environ.get("ORGANIZATION_DEFAULTS_FILE")
property_defaults_file_path = os.environ.get("PROPERTY_DEFAULTS_FILE")


@app.on_event("startup")
async def startup_event():
    if (
        atp_defaults_file_path is None
        or organization_defaults_file_path is None
        or property_defaults_file_path is None
    ):
        raise Exception(
            "Must provide environment variables ATP_DEFAULTS_FILE and ORGANIZATION_DEFAULTS_FILE"
        )

    adtech_platform_defaults[ATPTemplate.DSP] = AdTechPlatform.load_default_yaml(
        ATPTemplate.DSP.value, atp_defaults_file_path
    )
    adtech_platform_defaults[ATPTemplate.SSP] = AdTechPlatform.load_default_yaml(
        ATPTemplate.SSP.value, atp_defaults_file_path
    )
    adtech_platform_defaults[ATPTemplate.NETWORK] = AdTechPlatform.load_default_yaml(
        ATPTemplate.NETWORK.value, atp_defaults_file_path
    )
    organization_defaults[OrganizationType.GENERIC] = CorporateEmissions.load_default_yaml(
        OrganizationType.GENERIC.value, organization_defaults_file_path
    )
    organization_defaults[OrganizationType.PUBLISHER] = CorporateEmissions.load_default_yaml(
        OrganizationType.PUBLISHER.value, organization_defaults_file_path
    )
    organization_defaults[OrganizationType.ATP] = CorporateEmissions.load_default_yaml(
        OrganizationType.ATP.value, organization_defaults_file_path
    )
    property_defaults[PropertyTemplate.NEWS_WITH_PRINT] = Property.load_default_yaml(
        PropertyTemplate.NEWS_WITH_PRINT.value, property_defaults_file_path
    )


@app.get("/healthz")
def healthz():
    return "200 OK"


class CorporateInput(BaseModel):
    org_type: OrganizationType
    number_of_employees: Optional[int]
    office_emissions_mt_co2e_per_employee_per_month: Optional[float]
    datacenter_emissions_mt_co2e_per_employee_per_month: Optional[float]
    travel_emissions_mt_co2e_per_employee_per_month: Optional[float]
    commuting_emissions_mt_co2e_per_employee_per_month: Optional[float]
    overhead_emissions_mt_co2e_per_employee_per_month: Optional[float]
    corporate_emissions_mt_co2e_per_month: Optional[float]


@app.post("/calculate/corporate")
def calculate_corporate_emissions(data: CorporateInput):
    unmodeled = CorporateEmissions(
        data.office_emissions_mt_co2e_per_employee_per_month,
        data.datacenter_emissions_mt_co2e_per_employee_per_month,
        data.travel_emissions_mt_co2e_per_employee_per_month,
        data.commuting_emissions_mt_co2e_per_employee_per_month,
        data.overhead_emissions_mt_co2e_per_employee_per_month,
        data.corporate_emissions_mt_co2e_per_month,
        data.number_of_employees,
    )
    return unmodeled.comp_emissions_g_co2e_per_month(organization_defaults[data.org_type], 1)


class ATPInput(BaseModel):
    name: str = ""
    identifier: str = ""
    atp_template: ATPTemplate
    corporate_emissions_g_co2e: Optional[float]
    allocation_of_company_servers_pct: Optional[float] = 100
    allocation_of_corporate_emissions_pct: Optional[float] = 100
    corporate_emissions_g_co2e_per_bid_request: Optional[float]
    bid_requests_processed_from_ad_tech_platforms_pct: Optional[float]
    bid_request_size_in_bytes: Optional[float]
    server_to_server_emissions_g_co2e_per_gb: Optional[float]
    server_emissions_mt_co2e_per_month: Optional[float]
    servers_processing_bid_requests_pct: Optional[float]
    atp_block_rate: Optional[float]
    cookie_syncs_processed_per_bid_request: Optional[float]
    datacenter_water_intensity_h2o_m_3_per_mwh: Optional[float]
    server_emissions_g_co2e_per_kwh: Optional[float]
    servers_processing_cookie_syncs_pct: Optional[float]
    cookie_sync_distribution_ratio: Optional[float]
    bid_requests_processed_billion_per_month: Optional[float]
    ad_tech_platform_bid_requests_processed_billion_per_month: Optional[float]
    cookie_syncs_processed_billion_per_month: Optional[float]
    data_transfer_emissions_mt_co2e_per_month: Optional[float]


@app.post("/calculate/atp")
def calculate_atp_emissions(data: ATPInput):
    unmodeled = AdTechPlatform(
        data.allocation_of_company_servers_pct,
        data.allocation_of_corporate_emissions_pct,
        data.corporate_emissions_g_co2e_per_bid_request,
        data.bid_requests_processed_from_ad_tech_platforms_pct,
        data.bid_request_size_in_bytes,
        data.server_to_server_emissions_g_co2e_per_gb,
        data.server_emissions_mt_co2e_per_month,
        data.servers_processing_bid_requests_pct,
        data.atp_block_rate,
        data.cookie_syncs_processed_per_bid_request,
        data.datacenter_water_intensity_h2o_m_3_per_mwh,
        data.server_emissions_g_co2e_per_kwh,
        data.servers_processing_cookie_syncs_pct,
        data.cookie_sync_distribution_ratio,
        data.bid_requests_processed_billion_per_month,
        data.ad_tech_platform_bid_requests_processed_billion_per_month,
        data.cookie_syncs_processed_billion_per_month,
        data.data_transfer_emissions_mt_co2e_per_month,
    )
    return unmodeled.model_product(
        name=data.name,
        identifier=data.identifier,
        defaults=adtech_platform_defaults[data.atp_template],
        distribution_partners=[],
        corporate_emissions_g=data.corporate_emissions_g_co2e,
    )


class ATPSecondaryEmissionsInput(BaseModel):
    count: int = 1
    partners: list[DistributionPartner]


@app.post("/calculate/atp_secondary_bid_request_emissions")
def calculate_atp_secondary_bid_request_emissions(data: ATPSecondaryEmissionsInput):
    return data.count * AdTechPlatform().comp_secondary_emissions_g_co2e_per_bid_request(
        distribution_partners=data.partners, depth=1
    )


class ATPDefaultsResponse(BaseModel):
    template: str
    corporate_emissions_g_co2e_per_bid_request: Optional[float]
    atp_block_rate: float = 0.0
    publisher_block_rate: float = 0.0


@app.get("/defaults/atp/{template}")
def get_atp_template_defaults(template: ATPTemplate):
    defaults = adtech_platform_defaults[template]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_bid_request
    return ATPDefaultsResponse(
        template=template.value,
        corporate_emissions_g_co2e_per_bid_request=corporate_emissions,
        adtech_platform_block_rate=defaults.get_publisher_block_rate(),
        publisher_block_rate=defaults.get_atp_block_rate(),
    )


class PropertyDefaultsResponse(BaseModel):
    template: str
    corporate_emissions_g_co2e_per_impression: Optional[float]


@app.get("/defaults/property/{template}")
def get_property_template_defaults(template: PropertyTemplate):
    defaults = property_defaults[template]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_impression
    return PropertyDefaultsResponse(
        template=template.value,
        corporate_emissions_g_co2e_per_impression=corporate_emissions,
    )


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
