""" """

from pathlib import Path
from abc import ABC, abstractmethod
import json
import pandas as pd
import yaml
import ee
import polling2
import heet.monitor as mtr
import heet.task
import heet.log_setup
from heet.converters import Converter
from heet.assets import EmissionAssets
from heet.tasks import Task

assets = EmissionAssets()

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class ExporterInterface(ABC):
    """ """
    @abstractmethod
    def export(self) -> None:
        """Exports data to the source location."""


class EarthEngineExporter(ExporterInterface):
    """Exports assets within EarthEngine storage."""
    def export(self) -> None:
        pass


class GoogleDriveExporter(ExporterInterface):
    """Exports assets to Google Drive."""
    def export(self) -> None:
        pass


class LocalExporter(ExporterInterface):
    """Exports assets to local storage drive on the client side."""
    def export(self) -> None:
        pass


class Exporter(ExporterInterface):
    """ """
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.EXPORT_METHOD_CALLER = {
            ee.FeatureCollection: obj._export_ftc}
        return obj

    def __init__(self):
        self.exports = []

    def add_export(
            self,
            name: str,
            ft_collection: ee.FeatureCollection,
            ft_id) -> None:
        export = {
            "name": name,
            "data": ft_collection,
            "data_id": ft_id
        }
        self.exports.append(export)

    def export(self):
        """Run exports for all items in self.exports."""
        for export_dict in self.exports:
            name = export_dict["name"]
            message = "Exporting " + name
            id = export_dict["data_id"]
            data = export_dict["data"]
            logger.info(f'{message}, ID: {id}')
            # Export using differnt export functionality depending on the type
            # of data being exported
            self.EXPORT_METHOD_CALLER(type(data))(data, id, name)

    @staticmethod
    def _export_ftc(location_ftc, c_dam_id_str, jobtype):
        """ """
        # print ("[DEBUG] Exporting", c_dam_id_str, jobtype)
        job_id = export_job_specs[jobtype]["id"]
        job_desc = export_job_specs[jobtype]["desc"]
        job_fileprefix = export_job_specs[jobtype]["fileprefix"]
        job_taskcode = export_job_specs[jobtype]["taskcode"]

        if c_dam_id_str == "0":
            asset_id = assets.ps_heet_folder + "/" + job_fileprefix
        else:
            asset_id = assets.ps_heet_folder + "/" + job_fileprefix + c_dam_id_str

        task_config = {
            'collection': location_ftc,
            'description': "XHEET-X" + job_id + "-" + c_dam_id_str + " " + job_desc,
            'assetId': asset_id}

        task = Task(
            task_function=ee.batch.Export.table.toAsset,
            task_config=task_config)

        try:
            task.robust_start()
        except polling2.MaxCallException:
            logger.error(f"[export_ftc] Several attempts to start export {asset_id} failed. \
                         Possible connectivity issue. Export to assets skipped")
            if job_taskcode in mtr.critical_path:
                mtr.active_analyses.remove(int(c_dam_id_str))

        mtr.all_tasks_log[job_taskcode][c_dam_id_str] = task
        mtr.active_tasks_log[job_taskcode][c_dam_id_str] = task
        # print(mtr.all_tasks_log)


# ============================================================================
#  Export functions
# ============================================================================


export_job_specs = {
    "raw_dam_location":  {
        "id": "001", "desc": "Raw dam locations", "fileprefix": "PR_", "taskcode": "dam_pts"
    },
    "snapped_dam_location":  {
        "id": "002", "desc": "Snapped dam locations and upstream basins", "fileprefix": "PS_", "taskcode": "subbasin_pts"
    },
    "candidate_watershed_pts":  {
        "id": "003", "desc": "Candidate watershed points", "fileprefix": "CWPTS_", "taskcode": "watershed_cpts"
    },
    "detected_watershed_pts":  {
        "id": "004", "desc": "Detected watershed points", "fileprefix": "DWPTS_", "taskcode": "watershed_dpts"
    },
    "catchment_pixels":  {
        "id": "005", "desc": "Catchment pixels", "fileprefix": "CX_", "taskcode": "catch_pix"
    },
    "catchment_vector":  {
        "id": "006", "desc": "Catchment vector", "fileprefix": "c_", "taskcode": "catch_vec"
    },
    "catchment_vector_params":  {
        "id": "007", "desc": "Params catchment vector", "fileprefix": "C_", "taskcode": "catch_vec_params"
    },
    "waterbodies_pixels":  {
        "id": "008", "desc": "Waterbodies pixels", "fileprefix": "WBSX_", "taskcode": "wbs_pix"
    },
    "waterbodies_vector":  {
        "id": "009", "desc": "Waterbodies vector", "fileprefix": "WBS_", "taskcode": "wbs_vec"
    },
    "reservoir_vector":  {
        "id": "010", "desc": "Reservoir vector", "fileprefix": "r_", "taskcode": "res_vec"
    },
    "reservoir_vector_params":  {
        "id": "011", "desc": "Params reservoir vector", "fileprefix": "R_", "taskcode": "res_vec_params"
    },
    "ni_catchment_vector":  {
        "id": "012", "desc": "Non-inundated catchment vector", "fileprefix": "n_", "taskcode": "nic_vec"
    },
    "ni_catchment_vector_params":  {
        "id": "013", "desc": "Params non-inundated catchment vector", "fileprefix": "N_", "taskcode": "nic_vec_params"
    },
    "simple_reservoir_vector":  {
        "id": "014", "desc": "Simple reservoir vector", "fileprefix": "sr_", "taskcode": "sres_vec"
    },
    "simple_reservoir_boundary":  {
        "id": "015", "desc": "Simple reservoir boundary", "fileprefix": "rb_", "taskcode": "sres_bvec"
    },
    "river_vector":  {
        "id": "016", "desc": "All river vector", "fileprefix": "S_", "taskcode": "riv_vec"
    },
    "main_river_vector":  {
        "id": "017", "desc": "Main river vector", "fileprefix": "ms_", "taskcode": "mriv_vec"
    },
    "main_river_vector_params":  {
        "id": "018", "desc": "Params main river vector", "fileprefix": "MS_", "taskcode": "mriv_vec_params"
    },
    "river_sink_lines":  {
        "id": "019", "desc": "River sink lines", "fileprefix": "sl1_", "taskcode": "sink_vec"
    },
    "river_source_lines":  {
        "id": "020", "desc": "River source lines", "fileprefix": "sl2_", "taskcode": "source_vec"
    },
    "output_parameters":  {
        "id": "021", "desc": "All output parameters", "fileprefix": "output_parameters", "taskcode": "out_tab"
    },
    "debugging_vector":  {
        "id": "000", "desc": "A vector for debugging", "fileprefix": "debug_vector", "taskcode": "debug_vec"
    }
}


def prepare_output_table(df):

    d_lookup = {
        'any': 'str',
        'string': 'str',
        'number': 'float',
        'integer': 'int'
    }

    yaml_file_path = Path("utils", "outputs.resource.yaml")
    with yaml_file_path.open("r", encoding="utf-8") as ymlfile:
        profile = yaml.safe_load(ymlfile)

    # Add missing fields
    schema_fields = profile['schema']['fields']
    schema_field_names = [e['name'] for e in schema_fields]
    fields_detected = df.columns.to_list()

    # Filter out extra columns
    missing_fields = list(set(schema_field_names) - set(fields_detected))

    for fname in missing_fields:
        field_type = [e['type'] for e in schema_fields if e['name'] == fname]
        new_type = d_lookup[field_type[0]]

        df[fname] = pd.Series(dtype=new_type)

    # Order fields correctly
    df = df[schema_field_names].copy()

    return df


def download_output_parameters(output_folder_path):
    """ """
    try:
        asset_name = assets.ps_heet_folder + "/" + "output_parameters"
        output_parameters_ftc = ee.FeatureCollection(asset_name)
        df = Converter.ftc_to_df(output_parameters_ftc)
        df = prepare_output_table(df)
        df.to_csv(Path(output_folder_path, 'output_parameters.csv'), index=False)
        status = True
    except Exception as error:
        logger.exception("[download_output_parameters] Output parameters not downloaded")
        status = False
    return status


def asset_to_drive(asset_mta):

    asset_type = asset_mta['type']
    asset_name = asset_mta['name']

    item_name = asset_mta['name'].split("/")[-1]

    if asset_type == "TABLE":
        asset_ftc = ee.FeatureCollection(asset_name)
        if item_name in ["user_inputs", "output_parameters"]:
            file_format = 'CSV'
            asset_ftc = asset_ftc.map(lambda feat: feat.setGeometry(None))
        else:
            file_format = 'SHP'
            selected_properties = ee.List(["name", "id"])
            asset_ftc = asset_ftc.map(lambda feat: ee.Feature(feat).select(selected_properties))
        task_config = {
            'collection': asset_ftc,
            'folder': assets.output_drive_folder,
            'description': "XHEET-X011-0" + " Exporting to drive " + item_name,
            'fileFormat': file_format,
            'fileNamePrefix': item_name
        }

        task = Task(
            task_function=ee.batch.Export.table.toDrive,
            task_config=task_config)

    if asset_type == "IMAGE":

        file_format = 'GeoTIFF'

        asset_img = ee.Image(asset_name)
        projection = asset_img.select([0]).projection().getInfo()

        task_config = {
            'image': asset_img,
            'description': "XHEET-X011-0" + " Exporting to drive  " + item_name,
            'crs': projection['crs'],
            'crsTransform': projection['transform'],
            'fileNamePrefix': item_name
        }

        task = Task(
            task_function=ee.batch.Export.image.toDrive,
            task_config=task_config)

    try:
        task.robust_start()
    except polling2.MaxCallException:
        logger.error(f"[export_ftc] Several attempts to start export {item_name} \
                     to drive failed. Possible connectivity issue. Drive export Skipped")

    mtr.all_export_tasks_log[item_name] = task
    mtr.active_export_tasks_log[item_name] = task


def upload_user_inputs(inputs_ftc):
    """ """
    asset_id = assets.ps_heet_folder + "/" + "user_inputs"

    task_config = {
        'collection': inputs_ftc,
        'description': "XHEET-X000-0" + " User Inputs",
        'assetId': asset_id}

    task = Task(
        task_function=ee.batch.Export.table.toAsset,
        task_config=task_config)

    try:
        task.robust_start()
    except polling2.MaxCallException:
        logger.error(f"[export_ftc] Several attempts to start upload of {asset_id} failed. \
                     (Possible connectivity issue). Upload Skipped.")
    return task


def export_ftc(location_ftc, c_dam_id_str, jobtype):
    """ """
    # print ("[DEBUG] Exporting", c_dam_id_str, jobtype)
    job_id = export_job_specs[jobtype]["id"]
    job_desc = export_job_specs[jobtype]["desc"]
    job_fileprefix = export_job_specs[jobtype]["fileprefix"]
    job_taskcode = export_job_specs[jobtype]["taskcode"]

    if c_dam_id_str == "0":
        asset_id = assets.ps_heet_folder + "/" + job_fileprefix
    else:
        asset_id = assets.ps_heet_folder + "/" + job_fileprefix + c_dam_id_str

    task_config = {
        'collection': location_ftc,
        'description': "XHEET-X" + job_id + "-" + c_dam_id_str + " " + job_desc,
        'assetId': asset_id}

    task = Task(
        task_function=ee.batch.Export.table.toAsset,
        task_config=task_config)

    try:
        task.robust_start()
    except polling2.MaxCallException:
        logger.error(f"[export_ftc] Several attempts to start export {asset_id} failed. \
                     Possible connectivity issue. Export to assets skipped")
        if job_taskcode in mtr.critical_path:
            mtr.active_analyses.remove(int(c_dam_id_str))

    mtr.all_tasks_log[job_taskcode][c_dam_id_str] = task
    mtr.active_tasks_log[job_taskcode][c_dam_id_str] = task
    # print(mtr.all_tasks_log)


def export_image(location_img, c_dam_id_str, jobtype):
    """ """
    job_id = export_job_specs[jobtype]["id"]
    job_desc = export_job_specs[jobtype]["desc"]
    job_fileprefix = export_job_specs[jobtype]["fileprefix"]
    job_taskcode = export_job_specs[jobtype]["taskcode"]

    projection = location_img.select([0]).projection().getInfo()
    asset_id = assets.ps_heet_folder + "/" + job_fileprefix + c_dam_id_str

    task_config = {
        'image': location_img,
        'description': "XHEET-X" + job_id + "-" + c_dam_id_str + " " + job_desc,
        'assetId': asset_id,
        'crs': projection['crs'],
        'crsTransform': projection['transform']
    }

    task = Task(
        task_function=ee.batch.Export.table.toAsset,
        task_config=task_config)

    try:
        task.robust_start()
    except polling2.MaxCallException:
        logger.error(f"[export_ftc] Several attempts to start export {asset_id} failed. \
                     Possible connectivity issue. Export to assets skipped")
        if job_taskcode in mtr.critical_path:
            mtr.active_analyses.remove(int(c_dam_id_str))

    mtr.all_tasks_log[job_taskcode][c_dam_id_str] = task
    mtr.active_tasks_log[job_taskcode][c_dam_id_str] = task


def generate_empty_json_output():
    """ """
    entry = {
        "monthly_temps":
        [
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA",
            "NA"
        ],
        "catchment":
        {
            "runoff":  "NA",
            "area":  "NA",
            "population":  "NA",
            "area_fractions": [
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA"
            ],
            "slope": "NA",
            "precip":  "NA",
            "etransp":  "NA",
            "soil_wetness":  "NA",
            "biogenic_factors":
            {
                "biome":  "NONE",
                "climate": "NA",
                "soil_type": "NONE",
                "treatment_factor": "NONE",
                "landuse_intensity": "NONE"
            }
        },
        "reservoir": {
            "volume": "NA",
            "area": "NA",
            "max_depth": "NA",
            "mean_depth": "NA",
            "area_fractions": [
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA",
                "NA"
            ],
            "soil_carbon": "NA"
        }
    }

    return entry


def generate_json_output(out_ft):

    # The following categories are deliberately omitted in json
    # output (missing data categories).
    # - r_landcover_bysoil_0
    # - r_landcover_bysoil_9
    # - r_landcover_bysoil_18+

    missing_codes = ['ND', 'NA', 'UD', 'NONE', 'NODATA']

    entry = {
        "monthly_temps":
        [
            float(out_ft.get('r_mean_temp_1').getInfo()) if out_ft.get(
                'r_mean_temp_1').getInfo() not in missing_codes else out_ft.get('r_mean_temp_1').getInfo(),
            float(out_ft.get('r_mean_temp_2').getInfo()) if out_ft.get(
                'r_mean_temp_2').getInfo() not in missing_codes else out_ft.get('r_mean_temp_2').getInfo(),
            float(out_ft.get('r_mean_temp_3').getInfo()) if out_ft.get(
                'r_mean_temp_3').getInfo() not in missing_codes else out_ft.get('r_mean_temp_3').getInfo(),
            float(out_ft.get('r_mean_temp_4').getInfo()) if out_ft.get(
                'r_mean_temp_4').getInfo() not in missing_codes else out_ft.get('r_mean_temp_4').getInfo(),
            float(out_ft.get('r_mean_temp_5').getInfo()) if out_ft.get(
                'r_mean_temp_5').getInfo() not in missing_codes else out_ft.get('r_mean_temp_5').getInfo(),
            float(out_ft.get('r_mean_temp_6').getInfo()) if out_ft.get(
                'r_mean_temp_6').getInfo() not in missing_codes else out_ft.get('r_mean_temp_6').getInfo(),
            float(out_ft.get('r_mean_temp_7').getInfo()) if out_ft.get(
                'r_mean_temp_7').getInfo() not in missing_codes else out_ft.get('r_mean_temp_7').getInfo(),
            float(out_ft.get('r_mean_temp_8').getInfo()) if out_ft.get(
                'r_mean_temp_8').getInfo() not in missing_codes else out_ft.get('r_mean_temp_8').getInfo(),
            float(out_ft.get('r_mean_temp_9').getInfo()) if out_ft.get(
                'r_mean_temp_9').getInfo() not in missing_codes else out_ft.get('r_mean_temp_9').getInfo(),
            float(out_ft.get('r_mean_temp_10').getInfo()) if out_ft.get(
                'r_mean_temp_10').getInfo() not in missing_codes else out_ft.get('r_mean_temp_10').getInfo(),
            float(out_ft.get('r_mean_temp_11').getInfo()) if out_ft.get(
                'r_mean_temp_11').getInfo() not in missing_codes else out_ft.get('r_mean_temp_11').getInfo(),
            float(out_ft.get('r_mean_temp_12').getInfo()) if out_ft.get(
                'r_mean_temp_12').getInfo() not in missing_codes else out_ft.get('r_mean_temp_12').getInfo()
        ],
        "catchment":
        {
            "runoff": float(out_ft.get('c_mar_mm').getInfo()) if out_ft.get('c_mar_mm').getInfo() not in missing_codes else out_ft.get('c_mar_mm').getInfo(),
            "area": float(out_ft.get('c_area_km2').getInfo()) if out_ft.get('c_area_km2').getInfo() not in missing_codes else out_ft.get('c_area_km2').getInfo(),
            "population": float(out_ft.get('c_population').getInfo()) if out_ft.get('c_population').getInfo() not in missing_codes else out_ft.get('c_population').getInfo(),
            "area_fractions": [
                float(out_ft.get('c_landcover_1').getInfo()) if out_ft.get(
                    'c_landcover_1').getInfo() not in missing_codes else out_ft.get('c_landcover_1').getInfo(),
                float(out_ft.get('c_landcover_2').getInfo()) if out_ft.get(
                    'c_landcover_2').getInfo() not in missing_codes else out_ft.get('c_landcover_2').getInfo(),
                float(out_ft.get('c_landcover_3').getInfo()) if out_ft.get(
                    'c_landcover_3').getInfo() not in missing_codes else out_ft.get('c_landcover_3').getInfo(),
                float(out_ft.get('c_landcover_4').getInfo()) if out_ft.get(
                    'c_landcover_4').getInfo() not in missing_codes else out_ft.get('c_landcover_4').getInfo(),
                float(out_ft.get('c_landcover_5').getInfo()) if out_ft.get(
                    'c_landcover_5').getInfo() not in missing_codes else out_ft.get('c_landcover_5').getInfo(),
                float(out_ft.get('c_landcover_6').getInfo()) if out_ft.get(
                    'c_landcover_6').getInfo() not in missing_codes else out_ft.get('c_landcover_6').getInfo(),
                float(out_ft.get('c_landcover_7').getInfo()) if out_ft.get(
                    'c_landcover_7').getInfo() not in missing_codes else out_ft.get('c_landcover_7').getInfo(),
                float(out_ft.get('c_landcover_8').getInfo()) if out_ft.get(
                    'c_landcover_8').getInfo() not in missing_codes else out_ft.get('c_landcover_8').getInfo(),
            ],
            "slope": float(out_ft.get('c_mean_slope_pc').getInfo()) if out_ft.get('c_mean_slope_pc').getInfo() not in missing_codes else out_ft.get('c_mean_slope_pc').getInfo(),
            "precip": float(out_ft.get('c_map_mm').getInfo()) if out_ft.get('c_map_mm').getInfo() not in missing_codes else out_ft.get('c_map_mm').getInfo(),
            "etransp": float(out_ft.get('c_mpet_mm').getInfo()) if out_ft.get('c_mpet_mm').getInfo() not in missing_codes else out_ft.get('c_mpet_mm').getInfo(),
            "soil_wetness": float(out_ft.get('c_masm_mm').getInfo()) if out_ft.get('c_masm_mm').getInfo() not in missing_codes else out_ft.get('c_masm_mm').getInfo(),
            "biogenic_factors":
            {
                "biome": out_ft.get('c_biome').getInfo(),
                "climate": int(out_ft.get('c_climate_zone').getInfo()) if out_ft.get('c_climate_zone').getInfo() not in missing_codes else out_ft.get('c_climate_zone').getInfo(),
                "soil_type": out_ft.get('c_soil_type').getInfo(),
                "treatment_factor": "NA",
                "landuse_intensity": "NA"
            }
        },
        "reservoir": {
            "volume": float(out_ft.get('r_volume_m3').getInfo()) if out_ft.get('r_volume_m3').getInfo() not in missing_codes else out_ft.get('r_volume_m3').getInfo(),
            "area": float(out_ft.get('r_area_km2').getInfo()) if out_ft.get('r_area_km2').getInfo() not in missing_codes else out_ft.get('r_area_km2').getInfo(),
            "max_depth": float(out_ft.get('r_maximum_depth_m').getInfo()) if out_ft.get('r_maximum_depth_m').getInfo() not in missing_codes else out_ft.get('r_maximum_depth_m').getInfo(),
            "mean_depth": float(out_ft.get('r_mean_depth_m').getInfo()) if out_ft.get('r_mean_depth_m').getInfo() not in missing_codes else out_ft.get('r_mean_depth_m').getInfo(),
            "area_fractions": [
                float(out_ft.get('r_landcover_bysoil_1').getInfo()) if out_ft.get('r_landcover_bysoil_1').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_1').getInfo(),
                float(out_ft.get('r_landcover_bysoil_2').getInfo()) if out_ft.get('r_landcover_bysoil_2').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_2').getInfo(),
                float(out_ft.get('r_landcover_bysoil_3').getInfo()) if out_ft.get('r_landcover_bysoil_3').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_3').getInfo(),
                float(out_ft.get('r_landcover_bysoil_4').getInfo()) if out_ft.get('r_landcover_bysoil_4').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_4').getInfo(),
                float(out_ft.get('r_landcover_bysoil_5').getInfo()) if out_ft.get('r_landcover_bysoil_5').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_5').getInfo(),
                float(out_ft.get('r_landcover_bysoil_6').getInfo()) if out_ft.get('r_landcover_bysoil_6').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_6').getInfo(),
                float(out_ft.get('r_landcover_bysoil_7').getInfo()) if out_ft.get('r_landcover_bysoil_7').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_7').getInfo(),
                float(out_ft.get('r_landcover_bysoil_8').getInfo()) if out_ft.get('r_landcover_bysoil_8').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_8').getInfo(),
                float(out_ft.get('r_landcover_bysoil_10').getInfo()) if out_ft.get('r_landcover_bysoil_10').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_10').getInfo(),
                float(out_ft.get('r_landcover_bysoil_11').getInfo()) if out_ft.get('r_landcover_bysoil_11').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_11').getInfo(),
                float(out_ft.get('r_landcover_bysoil_12').getInfo()) if out_ft.get('r_landcover_bysoil_12').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_12').getInfo(),
                float(out_ft.get('r_landcover_bysoil_13').getInfo()) if out_ft.get('r_landcover_bysoil_13').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_13').getInfo(),
                float(out_ft.get('r_landcover_bysoil_14').getInfo()) if out_ft.get('r_landcover_bysoil_14').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_14').getInfo(),
                float(out_ft.get('r_landcover_bysoil_15').getInfo()) if out_ft.get('r_landcover_bysoil_15').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_15').getInfo(),
                float(out_ft.get('r_landcover_bysoil_16').getInfo()) if out_ft.get('r_landcover_bysoil_16').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_16').getInfo(),
                float(out_ft.get('r_landcover_bysoil_17').getInfo()) if out_ft.get('r_landcover_bysoil_17').getInfo(
                ) not in missing_codes else out_ft.get('r_landcover_bysoil_17').getInfo()
            ],
            "soil_carbon": float(out_ft.get('r_msoc_kgperm2').getInfo()) if out_ft.get('r_msoc_kgperm2').getInfo() not in missing_codes else out_ft.get('r_msoc_kgperm2').getInfo()
        }
    }

    return entry


def batch_export_to_json(output_folder_path):
    """ """
    dams_ftc = ee.FeatureCollection(assets.dams_table_path)
    c_dam_ids = dams_ftc.aggregate_array("id").getInfo()
    # Load output datasets
    # Catchment
    output_asset_name = assets.ps_heet_folder + "/" + "output_parameters"
    out_ftc = ee.FeatureCollection(output_asset_name)

    json_output = {}
    for c_dam_id in c_dam_ids:
        c_dam_id_str = str(c_dam_id)
        out_ft = (out_ftc.filter(
            ee.Filter.inList('id', ee.List([c_dam_id]))).first())
        entry = generate_json_output(out_ft)
        dam_name = "reservoir_" + c_dam_id_str
        json_output[dam_name] = entry

    json_object = json.dumps(json_output, indent=4)
    output_file_path = Path(output_folder_path, "output_parameters.json")
    with output_file_path.open("w", encoding="utf-8") as outfile:
        outfile.write(json_object)
