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
    EndUserDevices,
    OrganizationType,
    PropertyChannel,
)
from scope3_methodology.api.response_models import (
    ATPDefaultsResponse,
    PropertyDefaultsResponse,
)
from scope3_methodology.corporate.model import CorporateEmissions
from scope3_methodology.end_user_device.model import EndUserDevice
from scope3_methodology.publisher.model import Property
from scope3_methodology.utils.public_yaml_files import (
    PublicYamlInformation,
    get_all_public_yaml_files,
)
from scope3_methodology.utils.utils import get_facts
from scope3_methodology.utils.yaml_helpers import yaml_load

app = FastAPI()


@app.route("/")
@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    """Generate the redoc html for the API endpoints"""
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


public_yaml_files: dict[str, PublicYamlInformation] = get_all_public_yaml_files()
organization_defaults: dict[OrganizationType, CorporateEmissions] = {}
adtech_platform_defaults: dict[ATPTemplate, AdTechPlatform] = {}
property_defaults: dict[PropertyChannel, Property] = {}
end_user_device_defaults: dict[EndUserDevices, EndUserDevice] = {}


def load_default_files(
    adtech_platform_defaults_file: str,
    organization_defaults_file_path: str,
    property_defaults_file_path: str,
    end_user_device_file_path: str,
):
    """Load all default files into memory"""
    for atp_template in ATPTemplate:
        adtech_platform_defaults[atp_template] = AdTechPlatform.load_default_yaml(
            atp_template.value, adtech_platform_defaults_file
        )
    for org_type in OrganizationType:
        organization_defaults[org_type] = CorporateEmissions.load_default_yaml(
            org_type.value, organization_defaults_file_path
        )
    for channel in PropertyChannel:
        property_defaults[channel] = Property.load_default_yaml(
            "generic", property_defaults_file_path, channel.value
        )

    for device in EndUserDevices:
        end_user_device_defaults[device] = EndUserDevice.load_default_yaml(
            device.value, end_user_device_file_path
        )


@app.on_event("startup")
async def startup_event():
    """
    Startup will run before the API serves requests

    It will load:
    - all defatults for usage in calculating emissions
    - all public yaml files
    """

    atp_defaults_file_path = os.environ.get("ATP_DEFAULTS_FILE")
    organization_defaults_file_path = os.environ.get("ORGANIZATION_DEFAULTS_FILE")
    property_defaults_file_path = os.environ.get("PROPERTY_DEFAULTS_FILE")
    end_user_device_file_path = os.environ.get("END_USER_DEVICE_DEFAULTS_FILE")

    if (
        atp_defaults_file_path is None
        or organization_defaults_file_path is None
        or property_defaults_file_path is None
        or end_user_device_file_path is None
    ):
        raise Exception("Must provide environment variables for default files")

    load_default_files(
        atp_defaults_file_path,
        organization_defaults_file_path,
        property_defaults_file_path,
        end_user_device_file_path,
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


@app.get("/defaults/atp")
def get_all_atp_template_defaults():
    """
    Returns following defaults for a all ATP templates
        - corporate_emissions_g_co2e_per_bid_request
        - atp_block_rate
        - publisher_block_rate
    """
    response = []
    for template, defaults in adtech_platform_defaults.items():
        corporate_emissions = defaults.corporate_emissions_g_co2e_per_bid_request
        response.append(
            ATPDefaultsResponse(
                template=template.value,
                corporate_emissions_g_co2e_per_bid_request=corporate_emissions,
                adtech_platform_block_rate=defaults.get_atp_block_rate(),
                publisher_block_rate=defaults.get_publisher_block_rate(),
            )
        )
    return response


@app.get("/defaults/atp/{template}")
def get_atp_template_defaults(template: ATPTemplate):
    """
    Template options: dsp, ssp
    Returns following defaults for a specific ATP template
        - corporate_emissions_g_co2e_per_bid_request
        - atp_block_rate
        - publisher_block_rate
    """
    defaults = adtech_platform_defaults[template]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_bid_request
    return ATPDefaultsResponse(
        template=template.value,
        corporate_emissions_g_co2e_per_bid_request=corporate_emissions,
        adtech_platform_block_rate=defaults.get_atp_block_rate(),
        publisher_block_rate=defaults.get_publisher_block_rate(),
    )


@app.get("/defaults/property")
def get_all_property_template_defaults():
    """
    Returns corporate_emissions_g_co2e_per_impression default for all property channels
    """
    response = []
    for channel, defaults in property_defaults.items():
        corporate_emissions = defaults.corporate_emissions_g_co2e_per_impression
        response.append(
            PropertyDefaultsResponse(
                channel=channel.value,
                template="generic",
                corporate_emissions_g_co2e_per_impression=corporate_emissions,
            )
        )
    return response


@app.get("/defaults/property/{channel}")
def get_property_template_defaults(channel: PropertyChannel):
    """
    Channel options: display | streaming
    Returns following defaults for a specific property channel
        - right now there is only a single generic template for each channel
        - corporate_emissions_g_co2e_per_impressions
    """
    defaults = property_defaults[channel]
    corporate_emissions = defaults.corporate_emissions_g_co2e_per_impression
    return PropertyDefaultsResponse(
        channel=channel.value,
        template="generic",
        corporate_emissions_g_co2e_per_impression=corporate_emissions,
    )


@app.get("/public_yaml_files/list/{file_type}")
def get_public_yaml_files(file_type: str):
    """
    Returns a list of all <file_type> yaml files
    """
    files = []
    for file_info in public_yaml_files.values():
        if file_info.file_type == file_type:
            files.append(file_info)
    return files


@app.get("/public_yaml_files/parse/corporate/{identifier}")
def parse_corporate_public_yaml_file(identifier: str):
    """
    Returns a parsed corporate yaml file factual information
    """
    try:
        file_info = public_yaml_files[f"{identifier}corporate"]
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Unable to locate corporate file with '{identifier}'"
        ) from exc

    try:
        with open(file_info.file_path, "r", encoding="UTF-8") as stream:
            document = yaml_load(stream)
            if "name" not in document:
                raise Exception("No 'name' field found in company file")
            facts = get_facts(document["facts"]) if "facts" in document else {}
            info = CorporateEmissions(**facts)  # type: ignore
            return {
                "file_info": file_info,
                "facts": {
                    "commuting_emissions_mt_co2e_per_employee_per_month": info.commuting_emissions_mt_co2e_per_employee_per_month,
                    "overhead_emissions_mt_co2e_per_employee_per_month": info.overhead_emissions_mt_co2e_per_employee_per_month,
                    "corporate_emissions_mt_co2e_per_month": info.corporate_emissions_mt_co2e_per_month,
                    "travel_emissions_mt_co2e_per_employee_per_month": info.travel_emissions_mt_co2e_per_employee_per_month,
                    "number_of_employees": info.number_of_employees,
                    "office_emissions_mt_co2e_per_employee_per_month": info.office_emissions_mt_co2e_per_employee_per_month,
                    "datacenter_emissions_mt_co2e_per_employee_per_month": info.datacenter_emissions_mt_co2e_per_employee_per_month,
                },
            }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open and parse corporate file '{file_info.file_path}'",
        ) from exc


@app.get("/defaults/end_user_device")
def get_all_end_user_device_defaults():
    """
    Returns all end user device defaults
    """
    response = []
    for device, device_defaults in end_user_device_defaults.items():
        for channel, channel_defaults in property_defaults.items():
            if channel_defaults.quality_impressions_per_duration_s:
                modeled_end_user_device = device_defaults.model_end_user_device(
                    device.value,
                    channel.value,
                    "generic",
                    channel_defaults.quality_impressions_per_duration_s,
                )
                if modeled_end_user_device is not None:
                    response.append(modeled_end_user_device)
    return response


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
