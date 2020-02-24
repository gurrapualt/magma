#!/usr/bin/env python3
# @generated AUTOGENERATED file. Do not Change!

from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from numbers import Number
from typing import Any, Callable, List, Mapping, Optional

from dataclasses_json import dataclass_json
from marshmallow import fields as marshmallow_fields

from .datetime_utils import fromisoformat

from .add_location_input import AddLocationInput


DATETIME_FIELD = field(
    metadata={
        "dataclasses_json": {
            "encoder": datetime.isoformat,
            "decoder": fromisoformat,
            "mm_field": marshmallow_fields.DateTime(format="iso"),
        }
    }
)


@dataclass_json
@dataclass
class AddLocationMutation:
    __QUERY__ = """
    mutation AddLocationMutation($input: AddLocationInput!) {
  addLocation(input: $input) {
    id
    name
    latitude
    longitude
    externalId
    locationType {
      name
    }
  }
}

    """

    @dataclass_json
    @dataclass
    class AddLocationMutationData:
        @dataclass_json
        @dataclass
        class Location:
            @dataclass_json
            @dataclass
            class LocationType:
                name: str

            id: str
            name: str
            latitude: Number
            longitude: Number
            locationType: LocationType
            externalId: Optional[str] = None

        addLocation: Optional[Location] = None

    data: Optional[AddLocationMutationData] = None
    errors: Optional[Any] = None

    @classmethod
    # fmt: off
    def execute(cls, client, input: AddLocationInput):
        # fmt: off
        variables = {"input": input}
        response_text = client.call(cls.__QUERY__, variables=variables)
        return cls.from_json(response_text).data