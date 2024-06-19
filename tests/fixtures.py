# -*- coding: utf-8 -*-
import pytest
from typing import Dict


@pytest.fixture()
def ghg_outputs_dict(request) -> Dict:
    output_dict = {
        "coordinates": [22.6, 94.7],
        "monthly_temps": [10.56, 11.99, 15.46, 18.29, 20.79, 22.09, 22.46,
                          22.66, 21.93, 19.33, 15.03, 11.66],
        "year_vector": [1, 5, 10, 20, 30, 40, 50, 65, 80, 100],
        "gases": ["co2", "ch4", "n2o"],
        "catchment": {
            "runoff": 1685.5619,
            "area": 78203.0,
            "riv_length": 9.2,
            "population": 8463,
            "area_fractions": [0.0, 0.0, 0.0, 0.0, 0.0, 0.01092, 0.11996,
                               0.867257],
            "slope": 8.0,
            "precip": 2000.0,
            "etransp": 400.0,
            "soil_wetness": 140.0,
            "mean_olsen": 2.3,
            "biogenic_factors": {
                "biome": "TROPICALMOISTBROADLEAF",
                "climate": "TROPICAL",
                "soil_type": "MINERAL",
                "treatment_factor": "NONE",
                "landuse_intensity": "LOW"
            }
        },
        "reservoir": {
            "volume": 7663812,
            "area": 0.56470,
            "max_depth": 32.0,
            "mean_depth": 13.6,
            "area_fractions": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "soil_carbon": 10.228,
            "mean_radiance": 4.5,
            "mean_radiance_may_sept": 4.5,
            "mean_radiance_nov_mar": 3.2,
            "mean_monthly_windspeed": 3.8,
            "water_intake_depth": None
        }
    }
    return output_dict
