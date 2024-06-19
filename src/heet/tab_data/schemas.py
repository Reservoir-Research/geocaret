"""Wrapper object for frictionless framework schemas"""
from __future__ import annotations
import pathlib
import copy
import pandas as pd
from heet.utils import read_config


class Schema:
    """Wrapper object for Frictionless framework schemas."""
    def __init__(self, schema: dict):
        """ """
        self.schema = schema

    @classmethod
    def from_file(cls, file_name: pathlib.Path) -> Schema:
        """Load Schema object from schema config file."""
        return cls(schema=read_config(file_name=file_name))

    def adapt_to_data(self, data: pd.DataFrame) -> None:
        """
        Adapt validation schema to data to comform with frictionless
        framework requirements:

        Built in validation capability of frictionless data is very strict
        - column order is enforced.
        - optional columns are not supported
        To address this, we tailor a base validation schema to the input dataset.
        - We add any extra columns to the schema (no validation)
        - We reorder columns in the schema to reflect the data
        """
        updated_schema = copy.deepcopy(self.schema)
        template = {
            'name': 'Added Variable 1',
            'description': 'Custom variable',
            'type': 'any'}
        data_fields = data.columns.to_list()
        schema_fields = copy.deepcopy(self.schema['schema']['fields'])
        update_data_fields = []
        for field in data_fields:
            matched_fields = [e for e in schema_fields if e['name'] == field]
            if len(matched_fields) == 0:
                entry = template.copy()
                entry['name'] = field
            else:
                entry = matched_fields[0]
            update_data_fields.append(entry)
        updated_schema['schema']['fields'] = update_data_fields
        self.schema = updated_schema


if __name__ == '__main__':
    """ """
