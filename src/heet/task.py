""" """
import pathlib
import yaml
import re
import sys
import logging
import pandas as pd
from pathlib import Path

import ee
import polling2
from polling2 import poll_decorator

import heet.gis.basins
import heet.gis.catchment
import heet.gis.reservoir as heet_res
import heet.export
import heet.params
import heet.gis.river
import heet.monitor as mtr
import heet.log_setup
from heet.assets import EmissionAssets
from heet.jobs import Job
from heet.utils import load_packaged_data

assets = EmissionAssets()

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)

config_file: pathlib.PosixPath = load_packaged_data(
    './config/parameters.yaml')
with open(config_file, "r", encoding="utf8") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)['assets']

# ==============================================================================
# Polling functions
# ==============================================================================

# Wait a maximum of 30 minutes (1800)


@poll_decorator(step=5, timeout=1800)
def wait_until_upload(upload_task):

    keep_waiting = True
    try:
        status = upload_task.status()['state'] in ['COMPLETED', 'FAILED', 'CANCELLED']
    except:
        pass
    else:
        if status:
            keep_waiting = False

    return keep_waiting == False

# Wait a maximum of 90 minutes (5400)


@poll_decorator(step=5, timeout=5400)
def wait_until_jobs_finish():

    try:
        status = Job.existing_tasks_running()
    except:
        status = True

    return status == False

# Wait a maximum of 90 minutes (5400)


@poll_decorator(step=5, timeout=5400)
def wait_until_new_results():

    keep_waiting = True

    new_results_count = log_new_results()
    active_analysis_count = len(mtr.active_analyses)

    if new_results_count != 0:
        keep_waiting = False

    if active_analysis_count == 0:
        keep_waiting = False

    return keep_waiting == False

# Wait a maximum of 30 minutes (1800)


@poll_decorator(step=5, timeout=1800)
def wait_until_exports():

    try:
        new_exports_size = log_new_exports()
    except:
        new_exports_size = 0
    return new_exports_size != 0

# ==============================================================================
# Task functions
# ==============================================================================


def find_child_assets(search_list: list) -> list:
    """ Find assets on Earth Engine"""
    search_list = [a for a in search_list if a['type'] in
                   ["FOLDER", "IMAGECOLLECTION"]]

    new_asset_collection = []
    search_next = []

    for target_asset in search_list:
        found = ee.data.listAssets({'parent': target_asset['name']})
        if 'assets' in found:
            new_asset_collection.extend(found['assets'])
            search_next.extend(found['assets'])
    return search_next, new_asset_collection


def find_assets(search_list: list, asset_collection: list) -> list:
    """ Find assets on Earth Engine"""
    search_next, new_asset_collection = find_child_assets(search_list)
    asset_collection.extend(new_asset_collection)

    while len(search_next) > 0:
        search_next, new_asset_collection = find_child_assets(search_next)
        asset_collection.extend(new_asset_collection)

    return asset_collection


def assets_to_ftc():

    heet_assets = ee.data.listAssets({'parent': assets.ps_heet_folder})
    asset_collection = heet_assets['assets']
    dams_ftc = ee.FeatureCollection(assets.dams_table_path)
    c_dam_ids = dams_ftc.aggregate_array("id").getInfo()
    output_list = ee.List([])
    for c_dam_id in c_dam_ids:
        dam_feat = (
            ee.FeatureCollection(assets.dams_table_path)
            .filter(ee.Filter.inList('id', ee.List([c_dam_id]))))
        c_dam_id_str = str(c_dam_id)
        c_search_term = '.*/C_' + c_dam_id_str + '$'
        p_search_term = '.*/PS_' + c_dam_id_str + '$'
        r_search_term = '.*/R_' + c_dam_id_str + '$'
        n_search_term = '.*/N_' + c_dam_id_str + '$'
        s_search_term = '.*/MS_' + c_dam_id_str + '$'

        snapped_assets_list = ee.List(
            [ee.FeatureCollection(x['id'])
             for x in asset_collection if re.search(p_search_term, x['name'])]
        )

        catchment_assets_list = ee.List(
            [ee.FeatureCollection(x['id'])
             for x in asset_collection if re.search(c_search_term, x['name'])])

        reservoir_assets_list = ee.List(
            [ee.FeatureCollection(x['id'])
             for x in asset_collection if re.search(r_search_term, x['name'])])

        nicatchment_assets_list = ee.List(
            [ee.FeatureCollection(x['id'])
             for x in asset_collection if re.search(n_search_term, x['name'])])

        river_assets_list = ee.List(
            [ee.FeatureCollection(x['id'])
             for x in asset_collection if re.search(s_search_term, x['name'])])

        input_feat = dam_feat.first()
        output_feat = ee.Feature(None)

        drop_fields = [
            't_water_level',
            't_dam_height',
            't_turbine_efficiency',
            't_power_capacity',
            't_plant_depth',
            '_imputed_water_level',
            'outlet_subcatch_id',
            'CATCH_SKM',
            'DIST_DN_KM',
            'DIST_UP_KM',
            'DIS_AV_CMS',
            'ENDORHEIC',
            'HYBAS_L12',
            'HYRIV_ID',
            'LENGTH_KM',
            'MAIN_RIV',
            'NEXT_DOWN',
            'ORD_CLAS',
            'ORD_FLOW',
            'ORD_STRA',
            'UPLAND_SKM',
            'iolet',
            'is_sink',
            'is_source']

        # Properties from feature (inputted parameters)
        output_feat = input_feat.copyProperties(
            input_feat,
            None,
            drop_fields
        )

        status = 0
        if snapped_assets_list.length().getInfo() > 0:
            input_geom = ee.FeatureCollection(snapped_assets_list.get(0)).geometry()
            output_feat = output_feat.copyProperties(
                ee.FeatureCollection(snapped_assets_list.get(0)).first()
            )
            # Copy properties from feature collections
            # We use first to access collection level properties that have been duplicated over
            # all features.
            if catchment_assets_list.length().getInfo() > 0:
                output_feat = output_feat.copyProperties(
                    ee.FeatureCollection(catchment_assets_list.get(0)).first()
                )

                if reservoir_assets_list.length().getInfo() > 0:
                    output_feat = output_feat.copyProperties(
                        ee.FeatureCollection(reservoir_assets_list.get(0)).first()
                    )

                    if nicatchment_assets_list.length().getInfo() > 0:
                        output_feat = output_feat.copyProperties(
                            ee.FeatureCollection(nicatchment_assets_list.get(0)).first()
                        )

                        if river_assets_list.length().getInfo() > 0:
                            output_feat = output_feat.copyProperties(
                                ee.FeatureCollection(river_assets_list.get(0)).first()
                            )
                        else:
                            output_feat = output_feat.set(heet.params.profile_empty_river())
                            status = 5
                    else:
                        output_feat = output_feat.set(heet.params.profile_empty_nicatchment())
                        output_feat = output_feat.set(heet.params.profile_empty_river())
                        status = 4
                else:
                    output_feat = output_feat.set(heet.params.profile_empty_reservoir())
                    output_feat = output_feat.set(heet.params.profile_empty_nicatchment())
                    output_feat = output_feat.set(heet.params.profile_empty_river())
                    status = 3
            else:
                output_feat = output_feat.set(heet.params.profile_empty_catchment())
                output_feat = output_feat.set(heet.params.profile_empty_reservoir())
                output_feat = output_feat.set(heet.params.profile_empty_nicatchment())
                output_feat = output_feat.set(heet.params.profile_empty_river())
                status = 2

        else:
            # Use raw dam location if snap failed
            input_geom = dam_feat.first().geometry()
            output_feat = output_feat.set(heet.params.profile_empty_point())
            output_feat = output_feat.set(heet.params.profile_empty_catchment())
            output_feat = output_feat.set(heet.params.profile_empty_reservoir())
            output_feat = output_feat.set(heet.params.profile_empty_nicatchment())
            output_feat = output_feat.set(heet.params.profile_empty_river())
            status = 1

        output_feat = ee.Feature(output_feat).setGeometry(input_geom)
        output_feat = output_feat.set('error_code', ee.Number(status))
        output_list = ee.List(output_list).add(output_feat)

    output_assets_ftc = ee.FeatureCollection(output_list)

    heet.export.export_ftc(output_assets_ftc, "0", "output_parameters")


def export_to_drive():

    try:
        heet_assets = ee.data.listAssets({'parent': assets.ps_heet_folder})
        asset_collection = heet_assets['assets']

        logger.info(
            f"[export_to_drive] Found {str(len(asset_collection))} items in {assets.ps_heet_folder}")

        if len(asset_collection) > 0:
            assets_to_export = find_assets(heet_assets['assets'], asset_collection)
            assets_to_export.reverse()

            for target_asset in assets_to_export:
                asset_name = target_asset['name']
                logger.info(f"[export_to_drive] Exporting to Google Drive {asset_name}")
                heet.export.asset_to_drive(target_asset)

    except Exception as error:
        logger.exception("[export_to_drive] Problem Exporting to Google Drive")
        return False


def export_to_assets():

    target_asset_folder = assets.root_folder + "/" + \
        config.heet_folder.split("/")[0] + "/" + assets.output_asset_folder_name

    try:
        ee.data.createAsset({'type': 'Folder'}, target_asset_folder)
    except Exception as error:
        return False

    try:
        heet_assets = ee.data.listAssets({'parent': config.ps_heet_folder})
        asset_collection = heet_assets['assets']

        if len(asset_collection) > 0:
            assets_to_rename = find_assets(heet_assets['assets'], asset_collection)
            assets_to_rename.reverse()

            for target_asset in assets_to_rename:
                asset_name = target_asset['name']
                new_asset_name = re.sub(assets.ps_heet_folder, target_asset_folder, asset_name)

                ee.data.renameAsset(asset_name, new_asset_name)
        return True

    except Exception as error:
        return False


def task_audit(output_folder_path):

    target_dict = mtr.all_tasks_log
    target_dict['drive_export'] = mtr.all_export_tasks_log

    # Get an up-to-date list of all tasks submitted to EE
    # in this dict
    task_log_names = list(target_dict.keys())

    # Record task status in a dataframe
    task_log = []
    for task_log_name in task_log_names:

        task_dict = target_dict[task_log_name]

        for k, v in list(task_dict.items()):

            task_key = k
            task = v

            # Get task status
            try:
                task_status = task.status()

                if task_log_name != 'drive_export':
                    task_status['asset_name'] = task.config['assetExportOptions']['earthEngineDestination']['name']

            except:
                logger.debug(
                    f"[task_audit] There was a problem fetching task status for: {task_key}")
                task_status = {'state': 'UNKNOWN'}

            task_status['key'] = task_key
            task_status['task_code'] = task_log_name

            c_dam_id_str_list = re.findall('.*_(\d+)', task_key)
            if len(c_dam_id_str_list) > 0:
                task_status['dam_id'] = c_dam_id_str_list[0]
            else:
                task_status['dam_id'] = 0

            task_log.append(task_status)

    df_tasks = pd.DataFrame.from_dict(task_log, orient='columns')
    df_tasks.to_csv(
        Path(output_folder_path, 'tasks.csv'), index=False)

    return True


def log_new_exports():

    # Update active tasks
    new_exports_count = 0
    new_exports = []

    task_dict = mtr.active_export_tasks_log
    for k, v in list(task_dict.items()):

        item_name = k
        task = v

        # Get task status
        try:
            task_status = task.status()['state']
        except:
            task_status = 'UNKNOWN'

        # If completed,
        if task_status == 'COMPLETED':
            new_exports.append(item_name)
            mtr.active_exports.remove(item_name)
            del task_dict[item_name]

        # If
        if task_status == 'FAILED':
            new_exports.append(item_name)
            mtr.active_exports.remove(item_name)
            del task_dict[item_name]

        new_exports_count = new_exports_count + len(new_exports)

    return new_exports_count


def log_new_results():

    # Get an up-to-date list of active tasks
    # that are on the critical path
    task_log_names = mtr.critical_path

    new_results_count = 0

    for task_log_name in task_log_names:

        task_dict = mtr.active_tasks_log[task_log_name]
        new_results = []

        for k, v in list(task_dict.items()):

            c_dam_id_str = k
            task = v

            # Get task status
            try:
                task_status = task.status()['state']
            except:
                task_status = 'UNKNOWN'

            # If task has completed, log new result
            # remove from active tasks
            if task_status == 'COMPLETED':
                new_results.append(int(c_dam_id_str))
                del task_dict[c_dam_id_str]

            # If task has failed, remove from active tasks,
            # Remove dam from active analysis list
            # (as we only monitor tasks on the critical path
            # a failed job ends the analysis)
            if task_status == 'FAILED':
                del task_dict[c_dam_id_str]
                mtr.active_analyses.remove(int(c_dam_id_str))

        mtr.new_results_log[task_log_name] = new_results
        new_results_count = new_results_count + len(new_results)

        # Post new result count to mtr namespace
        mtr.new_results_count = new_results_count

    return new_results_count


def trigger_next_step():

    # ==============================================================================
    # [2]  Delineate catchment
    # [3]  Calculate catchment properties
    # [4]  Delineate reservoir
    # [5]  Calculate reservoir properties
    # [7]  Delineate NIC
    # [8]  Calculate NIC properties
    # [9]  Delineate river
    # [10] Calculate river properties
    # ==============================================================================

    # Final step in calculation terminates analysis prior to export
    if len(mtr.new_results_log['mriv_vec_params']) > 0:
        new_priver_ids = mtr.new_results_log['mriv_vec_params']
        heet.params.batch_delete_shapes(new_priver_ids, 'main_river_vector')

        for c_dam_id in new_priver_ids:
            mtr.active_analyses.remove(c_dam_id)

    # When delineated rivers arrive,
    # - calculate parameters.
    if len(mtr.new_results_log['mriv_vec']) > 0:
        new_river_ids = mtr.new_results_log['mriv_vec']
        heet.params.batch_profile_rivers(new_river_ids)

    # When nics with params arrive,
    # - delineate rivers
    if len(mtr.new_results_log['nic_vec_params']) > 0:
        logger.info("Delineating inundated rivers")
        new_pnic_ids = mtr.new_results_log['nic_vec_params']
        heet.river.batch_delineate_rivers(new_pnic_ids)
        heet.params.batch_delete_shapes(new_pnic_ids, 'ni_catchment_vector')

    # When nics without parameters arrive
    # - add parameters
    if len(mtr.new_results_log['nic_vec']) > 0:
        logger.info("Calculating NIC params")
        new_nic_ids = mtr.new_results_log['nic_vec']
        heet.params.batch_profile_nicatchments(new_nic_ids)

    # When res with parameters arrive
    # - delineate NICS
    # - clean up
    if len(mtr.new_results_log['res_vec_params']) > 0:
        logger.info("Delineating non-inundated catchments")
        new_preservoir_ids = mtr.new_results_log['res_vec_params']
        heet.catchment.batch_delineate_nicatchments(new_preservoir_ids)
        heet.params.batch_delete_shapes(new_preservoir_ids, 'reservoir_vector')

    # When res without parameters arrive:
      # - Add parameters
    if len(mtr.new_results_log['res_vec']) > 0:
        logger.info("Calculating Reservoir Params")
        new_reservoir_ids = mtr.new_results_log['res_vec']
        heet.params.batch_profile_reservoirs(new_reservoir_ids)

    # When catchments with params arrive
    # - delineate reservoirs
    # - clean up catchments without params
    if len(mtr.new_results_log['catch_vec_params']) > 0:
        logger.info("Delineating reservoirs")
        new_pcatchment_ids = mtr.new_results_log['catch_vec_params']
        heet_res.batch_delineate_reservoirs(new_pcatchment_ids)
        heet.params.batch_delete_shapes(new_pcatchment_ids, 'catchment_vector')

    # When delineated catchments arrive, add params
    if len(mtr.new_results_log['catch_vec']) > 0:
        logger.info("Calculating Catchment Params")
        new_catchment_ids = mtr.new_results_log['catch_vec']
        heet.params.batch_profile_catchments(new_catchment_ids)

    # When snapped points arrive, delineate catchments.
    if len(mtr.new_results_log['subbasin_pts']) > 0:
        logger.info("Delineating catchments")
        new_snapped_ids = mtr.new_results_log['subbasin_pts']
        heet.catchment.batch_delineate_catchments(new_snapped_ids)


def run_analysis(pbar):

    dams_ftc = ee.FeatureCollection(assets.dams_table_path)

    # Define active analyses
    mtr.active_analyses = c_dam_ids
    new_results_count = mtr.new_results_count

    # Initiate analysis by snapping dams to hydrorivers & finding upstream basins
    # for all dams in batch
    heet.basins.batch_find_upstream_basins(dams_ftc)

    # Monitor the EE task queue for complete or failed jobs
    # until the active analysis list is empty
    # (a dam is removed from the active list if any task on the
    # critcal path fails or the final task on the critcal path completes successfully)

    keep_going = 1
    while (len(mtr.active_analyses) > 0) and (keep_going == 1):

        if new_results_count == 0:
            logger.info("Waiting for new results to arrive...")
            try:
                wait_until_new_results()
            except polling2.TimeoutException:
                current_active_analyses = ','.join([str(i) for i in mtr.active_analyses])
                emsg = f"Analysis wait time limit exceeded. Cancelling all unfinished HEET tasks (active: {current_active_analyses}."
                logger.info(emsg)
                Job.kill_all_running_tasks()
                keep_going = 0
            except:
                logger.debug("HEET encountered an error and will exit")
                sys.exit("HEET encountered an error and will exit")

            pbar.update(mtr.new_results_count)

            logger.info("Triggering Next Analysis Step (after wait)")
            trigger_next_step()

        else:
            logger.info("Triggering Next Analysis Step (No wait)")
            trigger_next_step()

        new_results_count = heet.task.log_new_results()

        pbar.update(mtr.new_results_count)

    status = abs(keep_going-1)
    return status
