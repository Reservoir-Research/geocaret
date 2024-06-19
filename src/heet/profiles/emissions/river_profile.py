""" """
from typing import Dict
from heet.profiles.profile import Profile
from heet.profiles.profile_output import ProfileOutput

REQUIRED_VARIABLES: Dict[str, str] = {"ms_length": "NA"}


class RiverProfile(Profile):
    """ """

    def populate(self) -> ProfileOutput:
        """ """
