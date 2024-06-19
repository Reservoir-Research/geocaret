import ee

# ==============================================================================
# Task monitoring
# ==============================================================================

# Monitoring Dam Analysis Calculations
active_analyses = []

critical_path = [
    'subbasin_pts',
    'catch_vec',
    'catch_vec_params',
    'res_vec',
    'res_vec_params',
    'nic_vec',
    'nic_vec_params',
    'mriv_vec',
    'mriv_vec_params'
]

active_tasks_log = {
    'dam_pts': {},
    'subbasin_pts': {},
    'watershed_cpts': {},
    'watershed_dpts': {},
    'catch_pix': {},
    'catch_vec': {},
    'catch_vec_params': {},
    'wbs_pix': {},
    'wbs_vec': {},
    'res_vec': {},
    'res_vec_params': {},
    'sres_vec': {},
    'mriv_vec': {},
    'mriv_vec_params': {},
    'sink_vec': {},
    'trunc_sink_vec': {},
    'source_vec': {},
    'trunc_source_vec': {},
    'riv_vec': {},
    'nic_vec': {},
    'nic_vec_params': {},
    'out_tab': {}
}

all_tasks_log = {
    'dam_pts': {},
    'subbasin_pts': {},
    'watershed_cpts': {},
    'watershed_dpts': {},
    'catch_pix': {},
    'catch_vec': {},
    'catch_vec_params': {},
    'wbs_pix': {},
    'wbs_vec': {},
    'res_vec': {},
    'res_vec_params': {},
    'sres_vec': {},
    'mriv_vec': {},
    'mriv_vec_params': {},
    'sink_vec': {},
    'trunc_sink_vec': {},
    'source_vec': {},
    'trunc_source_vec': {},
    'riv_vec': {},
    'nic_vec': {},
    'nic_vec_params': {},
    'out_tab': {}
}

new_results_log = {
    'dam_pts': [],
    'subbasin_pts': [],
    'watershed_cpts': [],
    'watershed_dpts': [],
    'catch_pix': [],
    'catch_vec': [],
    'catch_vec_params': [],
    'wbs_pix': [],
    'wbs_vec': [],
    'res_vec': [],
    'res_vec_params': [],
    'sres_vec': [],
    'mriv_vec': [],
    'mriv_vec_params': [],
    'sink_vec': [],
    'trunc_sink_vec': [],
    'source_vec': [],
    'trunc_source_vec': [],
    'riv_vec': [],
    'nic_vec': [],
    'nic_vec_params': [],
    'out_tab': []
}

new_results_count = 0

# Monitoring Exports to Google Drive

active_exports = []

active_export_tasks_log = {}
all_export_tasks_log = {}
