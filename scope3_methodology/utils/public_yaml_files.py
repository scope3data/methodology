""" Util functions to get public yaml files """

from glob import glob
from typing import Optional

from scope3_methodology.utils.yaml_helpers import yaml_load


class PublicYamlInformation:
    """Public Yaml File Information"""

    def __init__(
        self,
        public_identifier: str,
        file_type: Optional[str],
        name: Optional[str],
        template: Optional[str],
        file_path: str,
    ) -> None:
        self.public_identifier = public_identifier
        self.file_type = file_type
        self.name = name
        self.file_path = file_path
        self.template = template

    def __repr__(self):
        return f"{self.public_identifier}-{self.file_type} ({self.file_path})"


def get_all_public_yaml_files() -> dict[str, PublicYamlInformation]:
    """
    Return a dictionary of all public yaml files.
    Key: identifier
    Value: File Information
    """

    public_file_info = {}
    public_files = glob("data/companies/*/*.yaml")
    for file in public_files:
        with open(file, "r", encoding="UTF-8") as stream:
            document = yaml_load(stream)
            if "public_identifier" in document and "type" in document:
                identifier = document["public_identifier"]
                file_type = document["type"]
                public_file_info[f"{identifier}{file_type}"] = PublicYamlInformation(
                    public_identifier=identifier,
                    file_type=file_type,
                    name=document["name"] if "name" in document else None,
                    file_path=file,
                    template=document["template"] if "template" in document else None,
                )

    return public_file_info
