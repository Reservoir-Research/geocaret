""" """
from typing import Dict
from heet.profiles.profile import Profile
from heet.profiles.profile_output import ProfileOutput

REQUIRED_VARIABLES: Dict[str, str] = {
    "n_population": "NA",
    "n_population_density": "NA"}


class NiCatchmentProfile(Profile):
    """ """

    def populate(self) -> ProfileOutput:
        """ """
