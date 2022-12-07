""" Model for computing corporate emissions for an organization """

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from scope3_methodology.utils.constants import G_PER_MT
from scope3_methodology.utils.custom_base_model import CustomBaseModel
from scope3_methodology.utils.utils import log_result, not_none


@dataclass
class CorporateEmissions(CustomBaseModel):
    """Raw emissions information about an org and methodology of how to calculate emissions"""

    office_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    datacenter_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    travel_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    commuting_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    overhead_emissions_mt_co2e_per_employee_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": True}
    )
    corporate_emissions_mt_co2e_per_month: Optional[Decimal] = field(
        default=None, metadata={"default_eligible": False}
    )
    number_of_employees: Optional[int] = field(default=None, metadata={"default_eligible": False})
    defaults: Optional["CorporateEmissions"] = field(
        default=None, metadata={"default_eligible": False}
    )

    def set_defaults(self, defaults: "CorporateEmissions"):
        """Set defaults to be used as fallback in computations"""
        self.defaults = defaults

    def validate(self) -> None:
        """Validate the required CorporateEmissions fields for computation"""
        if not self.number_of_employees and not self.corporate_emissions_mt_co2e_per_month:
            raise Exception(
                """
                Unable to compute corporate emissions. Must provide either:
                    number_of_employees OR corporate_emissions_mt_co2e_per_month
                When computing atp or publisher model will use defaults.
                """
            )

    def comp_emissions_mt_co2e_per_month(
        self, defaults: "CorporateEmissions", depth: int
    ) -> Decimal | None:
        """Computes the corporate emisisons per month in metric tons CO2e"""
        self.validate()
        self.set_defaults(defaults)
        corporate_emissions = self.corporate_emissions_mt_co2e_per_month
        if corporate_emissions is None and self.number_of_employees:
            corporate_emissions = self.number_of_employees * (
                not_none(self.office_emissions_mt_co2e_per_employee_per_month)
                + not_none(self.travel_emissions_mt_co2e_per_employee_per_month)
                + not_none(self.datacenter_emissions_mt_co2e_per_employee_per_month)
                + not_none(self.commuting_emissions_mt_co2e_per_employee_per_month)
                + not_none(self.overhead_emissions_mt_co2e_per_employee_per_month)
            )
        log_result("corporate emissions mt co2e per month", f"{corporate_emissions:.2f}", depth)
        return corporate_emissions

    def comp_emissions_g_co2e_per_month(
        self, defaults: "CorporateEmissions", depth: int
    ) -> Decimal | None:
        """Computes the corporate emisisons per month in grams CO2e"""
        self.validate()
        self.set_defaults(defaults)
        corporate_emissions_mt = self.comp_emissions_mt_co2e_per_month(defaults, depth)
        if corporate_emissions_mt:
            corporate_emissions = corporate_emissions_mt * G_PER_MT
            log_result("corporate emissions g co2e per month", f"{corporate_emissions:.2f}", depth)
            return corporate_emissions
        return None
