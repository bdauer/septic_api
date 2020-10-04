"""
Generic mappings for fields.

These mappings are used to make sure that the data we retrieve
"""
from enum import Enum


class GenericSewerMappings(Enum):
    septic = "septic"
    municipal = "municipal"
    storm = "storm"
    type_unknown = "type_unknown"
    existence_unknown = "existence_unknown"
    no_sewer = "no_sewer"

class GenericFieldsToMappings(Enum):
    sewer = GenericSewerMappings
