"""
The HomeDataSvc combines fetching, parsing and normalizing.
In a real world scenario I'd consider decoupling those
into their own layers,
passed into the service's `__init__` and set as an attribute.
The service would perform delegation and store shared data.
"""
import abc
from enum import Enum

import requests

from common.mappings import GenericSewerMappings, GenericFieldsToMappings


class HouseCanarySewerPropertyDetails(Enum):
    """
    This enum helps to ensure that we're getting expected values.
    """
    # Could have used multiple values instead of the mapping dictionary further below
    # to save on boilerplate. Example:
    #   `municipal = ("Municipal", GenericSewerMappings.municipal.value)`
    # That would combine parsing with normalizing.
    # It would be more difficult to split those functionalities out later.
    municipal = "Municipal"
    septic = "Septic"
    storm = "Storm"
    none = "None"
    Yes = "Yes"


class HouseCanaryFields(Enum):
    sewer = HouseCanarySewerPropertyDetails


house_canary_field_to_generic = {
    HouseCanaryFields.sewer.name: GenericFieldsToMappings.sewer,
}

house_canary_sewer_to_generic = {
    HouseCanarySewerPropertyDetails.municipal.value: GenericSewerMappings.municipal.value,
    HouseCanarySewerPropertyDetails.septic.value: GenericSewerMappings.septic.value,
    HouseCanarySewerPropertyDetails.storm.value: GenericSewerMappings.storm.value,
    HouseCanarySewerPropertyDetails.none.value: GenericSewerMappings.no_sewer.value,
    HouseCanarySewerPropertyDetails.Yes.value: GenericSewerMappings.type_unknown.value
}


class HomeDataSvc(abc.ABC):
    """
    Abstract class for handling home data.
    """
    data = None

    # Limit fields to those that are currently supported.
    fields_to_retrieve = []

    # Fields calculated based on other fields.
    # Add as a method with the same name.
    constructed_fields = ['has_septic']

    def __init__(self, expected_fields, address, zip_code):
        self.expected_fields = expected_fields
        self.address = address
        self.zip_code = zip_code

    # The class could build home data on initialization
    # instead of via an external call to build_home_data.
    # Keeping those steps split out will make it easier to add steps prior to fetching data if needed.
    def build_home_data(self) -> dict:
        """
        Returns home data and sets data on the instance.
        """
        fetched_data = self.fetch_home_data()
        self.save_to_file(fetched_data)
        parsed_data = self.parse_home_data(fetched_data)
        normalized_data = self.normalize_home_data(parsed_data)
        data_with_constructed_fields = self._build_constructed_fields(normalized_data)
        pruned_data = {key: val for key, val in data_with_constructed_fields.items() if key in self.expected_fields}
        self.data = pruned_data
        return self.data

    def has_septic(self, data) -> bool:
        """
        Constructed field constructor.
        """
        sewer_key = GenericFieldsToMappings.sewer.name
        return data[sewer_key] == GenericSewerMappings.septic.value

    def _build_constructed_fields(self, normalized_data):
        """
        Data is normalized before constructing fields.
        Generic keys and values should be used when implementing field constructors.
        """
        for constructed_field in self.constructed_fields:
            try:
                field_constructor = getattr(self, constructed_field)
                normalized_data[constructed_field] = field_constructor(normalized_data)
            except AttributeError:
                # There could be good data in the fields that were requested and found
                # for an endpoint that doesn't support the constructed field's dependencies.
                continue
        return normalized_data

    def save_to_file(self, fetched_data):
        """
        Save the endpoint data to S3 or similar
        to help isolate the problem when something goes wrong.
        """
        pass

    @abc.abstractmethod
    def fetch_home_data(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def parse_home_data(self, home_data):
        raise NotImplementedError()

    @abc.abstractmethod
    def normalize_home_data(self, home_data):
        raise NotImplementedError()

    def save_to_database(self, home_data):
        """
        Similar to save_to_file, this would be where the normalized data is written to the database.
        I don't think there are any performance concerns with writing before returning a response,
        but if it became an issue this could run in a separate process.
        """
        pass

# If this file began to have more than a couple data sources
# it would be helpful to split the child classes into their own files.


class HouseCanaryHomeDataSvc(HomeDataSvc):
    """
    Service for fetching data from House Canary.
    """
    fields_to_retrieve = [HouseCanaryFields.sewer.name]

    def fetch_home_data(self):
        url = 'http://virtserver.swaggerhub.com/bdauer8/septic/1/canary'
        params = {
            'address': self.address,
            'zipcode': self.zip_code
        }
        # Normally I'd have an actual api key and secret, and I'd store them outside of the code.
        response = requests.get(url, params=params, auth=('my_api_key', 'my_api_secret'), timeout=7)
        response.raise_for_status()
        # In the real world I might check against the `api_code` returned as part of the payload.
        return response.json()

    def parse_home_data(self, home_data):
        """
        Parsing is pretty straightforward since we get json-encoded data.
        """
        # This would probably be better caught and raised with a new exception.
        # If the key is missing then something's changed in the schema.
        result = home_data['property/details']['result']
        property_data = result.get('property', {})
        property_assessment = result.get('assessment', {})
        property_data.update(property_assessment)
        return_val = {key: value for key, value in property_data.items() if key in self.fields_to_retrieve}
        return return_val

    def normalize_home_data(self, home_data):
        """
        Sets the parsed data to generic values.
        """
        normalized_home_data = {}
        for field_name, value in home_data.items():
            field_validator = HouseCanaryFields[field_name].value
            field_validator(value)
            normalized_field = house_canary_field_to_generic[field_name]
            normalized_field_name = normalized_field.name
            # Could use a defaultdict when building the mappings instead of setting a default on `get`
            # or add to the enum as `__missing__`. One downside of all of these approaches:
            # an unrecognized value won't raise an exception.
            normalized_field_value = house_canary_sewer_to_generic.get(
                value, GenericSewerMappings.existence_unknown.value
            )
            normalized_home_data[normalized_field_name] = normalized_field_value
        return normalized_home_data
