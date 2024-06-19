"""Custom exceptions used in the gis module."""


class NoOutletPointException(Exception):
    """Exception raised if no outlet point is define in the HydroBasins class.

    Attributes:
        message: explanation of the error
    """
    def __init__(
            self,
            message="Cannot find outlet subcatchment because outlet point " +
            "(e.g. dam) has not been defined."):
        self.message = message
        super().__init__(self.message)
