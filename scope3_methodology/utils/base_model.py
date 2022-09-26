""" Base Model that is inherited by publisher, ad tech platform and corporate models"""

from dataclasses import dataclass, fields

import yaml


@dataclass
class BaseModel:
    """Base Model"""

    @classmethod
    def default_fields(cls):
        """Retun all default fields of a model"""
        return [f.name for f in fields(cls) if f.metadata.get("default_eligible")]

    @classmethod
    def load_default_yaml(cls, template: str, defaults_file: str):
        """
        Takes a yaml file and loads in all default facts into the
        fields eligible for default
        """
        with open(defaults_file, "r") as defaults_stream:
            defaults_document = yaml.safe_load(defaults_stream)

            if template not in defaults_document["defaults"]:
                raise Exception(f"Template {template} not found in defaults")
            defaults: dict[str, float] = defaults_document["defaults"][template]
            keys = [f.name for f in fields(cls) if f.metadata.get("default_eligible")]
            return cls(**{k: v for k, v in defaults.items() if k in keys})

    def __getattribute__(self, name):
        if object.__getattribute__(self, name) is not None:
            return object.__getattribute__(self, name)

        default_eligible = [
            f.name for f in fields(object.__class__(self)) if f.metadata.get("default_eligible")
        ]
        if object.__getattribute__(self, "defaults") and name in default_eligible:
            default = object.__getattribute__(object.__getattribute__(self, "defaults"), name)
            if default is not None:
                return default
            raise Exception(f"Failed to find value or default for {name}")

        return None
