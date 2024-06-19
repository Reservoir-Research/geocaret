""" """
from typing import Dict
from heet.profiles.profile import Profile
from heet.profiles.profile_output import ProfileOutput


REQUIRED_VARIABLES: Dict[str, str] = {
    "ps_snap_displacement": "NA",
    "ps_lon": "NA",
    "ps_lat": "NA"}


class PointProfile(Profile):
    """ """

    def populate(self) -> ProfileOutput:
        """ """


if __name__ == '__main__':
    point_profile = PointProfile(gis_object="")

    # Insantiating by name
    module = __import__(__name__)
    class_ = getattr(module, "PointProfile")
    instance = class_(gis_object = "")
