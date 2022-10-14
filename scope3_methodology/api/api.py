# flake8: noqa

""" Expose a simple API for calculating emissions and pulling in computed defaults """
import os
from decimal import Decimal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_redoc_html

from scope3_methodology.ad_tech_platform.model import AdTechPlatform
from scope3_methodology.api.input_models import (
    ATPInput,
    ATPSecondaryEmissionsInput,
    ATPTemplate,
    CorporateInput,
    OrganizationType,
    PropertyTemplate,
)
from scope3_methodology.api.response_models import (
    ATPDefaultsResponse,
    PropertyDefaultsResponse,
)
from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.publisher.model import Property

app = FastAPI()


@app.route("/")
@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    """Generate the redoc html for the API endpoints"""
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


organization_defaults: dict[OrganizationType, CorporateEmissions] = {}
adtech_platform_defaults: dict[ATPTemplate, AdTechPlatform] = {}
property_defaults: dict[PropertyTemplate, Property] = {}
atp_defaults_file_path = os.environ.get("ATP_DEFAULTS_FILE")
organization_defaults_file_path = os.environ.get("ORGANIZATION_DEFAULTS_FILE")
property_defaults_file_path = os.environ.get("PROPERTY_DEFAULTS_FILE")


@app.on_event("startup")
async def startup_event():
    """
    Startup will run before the API serves requests. It will load in all
    defatults for usage in calculating emissions.
    """
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
    """/healthz always returns 200 OK"""
    return "200 OK"


@app.post("/calculate/corporate")
def calculate_corporate_emissions(data: CorporateInput):
    """Returns computed corporate emissions for an organization in g co2e"""
    unmodeled = CorporateEmissions(
        office_emissions_mt_co2e_per_employee_per_month=data.office_emissions_mt_co2e_per_employee_per_month,
        datacenter_emissions_mt_co2e_per_employee_per_month=data.datacenter_emissions_mt_co2e_per_employee_per_month,
        travel_emissions_mt_co2e_per_employee_per_month=data.travel_emissions_mt_co2e_per_employee_per_month,
        commuting_emissions_mt_co2e_per_employee_per_month=data.commuting_emissions_mt_co2e_per_employee_per_month,
        overhead_emissions_mt_co2e_per_employee_per_month=data.overhead_emissions_mt_co2e_per_employee_per_month,
        corporate_emissions_mt_co2e_per_month=data.corporate_emissions_mt_co2e_per_month,
        number_of_employees=data.number_of_employees,
    )

    return unmodeled.comp_emissions_g_co2e_per_month(organization_defaults[data.org_type], 1)


@app.post("/calculate/atp_primary_emissions")
def calculate_atp_emissions(data: ATPInput):
    """Returns computed primary emissions for an ad tech platform in g co2e"""
    if data.atp_template == ATPTemplate.NETWORK:
        raise HTTPException(
            status_code=501, detail="calculate_atp_emissions is not supported for NETWORK"
        )

    company_servers_pct = (
        data.allocation_of_company_servers_pct
        if data.allocation_of_company_servers_pct
        else Decimal("100.0")
    )
    corporate_emissions_pct = (
        data.allocation_of_corporate_emissions_pct
        if data.allocation_of_corporate_emissions_pct
        else Decimal("100.0")
    )
    unmodeled = AdTechPlatform(
        allocation_of_company_servers_pct=company_servers_pct,
        allocation_of_corporate_emissions_pct=corporate_emissions_pct,
        corporate_emissions_g_co2e_per_bid_request=data.corporate_emissions_g_co2e_per_bid_request,
        bid_requests_processed_from_ad_tech_platforms_pct=data.bid_requests_processed_from_ad_tech_platforms_pct,
        bid_requests_processed_from_publishers_pct=data.bid_requests_processed_from_publishers_pct,
        bid_request_size_in_bytes=data.bid_request_size_in_bytes,
        server_to_server_emissions_g_co2e_per_gb=data.server_to_server_emissions_g_co2e_per_gb,
        server_emissions_mt_co2e_per_month=data.server_emissions_mt_co2e_per_month,
        servers_processing_bid_requests_pct=data.servers_processing_bid_requests_pct,
        cookie_syncs_processed_per_bid_request=data.cookie_syncs_processed_per_bid_request,
        datacenter_water_intensity_h2o_m_3_per_mwh=data.datacenter_water_intensity_h2o_m_3_per_mwh,
        server_emissions_g_co2e_per_kwh=data.server_emissions_g_co2e_per_kwh,
        servers_processing_cookie_syncs_pct=data.servers_processing_cookie_syncs_pct,
        cookie_sync_distribution_ratio=data.cookie_sync_distribution_ratio,
        bid_requests_processed_billion_per_month=data.bid_requests_processed_billion_per_month,
        cookie_syncs_processed_billion_per_month=data.cookie_syncs_processed_billion_per_month,
        data_transfer_emissions_mt_co2e_per_month=data.data_transfer_emissions_mt_co2e_per_month,
    )

    return unmodeled.model_product(
        name=data.name,
        identifier=data.identifier,
        defaults=adtech_platform_defaults[data.atp_template],
        distribution_partners=[],
        corporate_emissions_g=data.corporate_emissions_g_co2e,
    )


@app.post("/calculate/atp_secondary_bid_request_emissions")
def calculate_atp_secondary_bid_request_emissions(data: ATPSecondaryEmissionsInput):
    """
    Returns computed secondary emissions for an ad tech platforms distribution partners in g co2e
    """
    return AdTechPlatform().comp_secondary_emissions_g_co2e_per_bid_request(
        distribution_partners=data.partners, depth=1
    )


@app.get("/defaults/atp/{template}")
def get_atp_template_defaults(template: ATPTemplate):
    """
    Template options: dsp, ssp
    Returns following defaults for a specific ATP template
        - corporate_emissions_g_co2e_per_bid_request
        - atp_block_rate
        - publisher_block_rate
    """
    if template == ATPTemplate.NETWORK:
        raise HTTPException(status_code=501, detail=f"/defaults/atp/{template} is not supported")

    defaults = adtech_platform_defaults[template]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_bid_request
    return ATPDefaultsResponse(
        template=template.value,
        corporate_emissions_g_co2e_per_bid_request=corporate_emissions,
        adtech_platform_block_rate=defaults.get_atp_block_rate(),
        publisher_block_rate=defaults.get_publisher_block_rate(),
    )


@app.get("/defaults/property/{template}")
def get_property_template_defaults(template: PropertyTemplate):
    """
    Template options: news_with_print
    Returns following defaults for a specific property template
        - corporate_emissions_g_co2e_per_impressions
    """
    defaults = property_defaults[template]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_impression
    return PropertyDefaultsResponse(
        template=template.value,
        corporate_emissions_g_co2e_per_impression=corporate_emissions,
    )


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
