## tab_data

This module contains functionality for converting, transforming and validating
tabular data and, in particular, input and output data used by the application.

It provides the methods for:
  * Converting tabular data between pandas dataframe format and different
      file formats - see ```converters.py```.
  * Transforming tabular data by converting field types and filling in and
      replacing values and missing fields in table fields - see ```transformers.py```.
  * Modifying frictionless schemas using ```Schema.adapt_to_data``` method, so that they match the structure of the
      tabular data
  * Validating tabular data using frictionless framework's capabilities.
  * Creating custom validation objects inheriting from ```Validation``` abstract base class that are then used by the frictionless framework.
