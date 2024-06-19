import logging
import ee

try:
    from delineator import heet_config as cfg
    from delineator import heet_data as dta
    from delineator import heet_export
    from delineator import heet_monitor as mtr
    from delineator import heet_snap
    from delineator import heet_log as lg
except ModuleNotFoundError:
    if not ee.data._credentials:
        ee.Initialize()

    import heet_config as cfg
    import heet_data as dta
    import heet_export
    import heet_monitor as mtr
    import heet_snap
    import heet_log as lg
debug_mode = False

# ==============================================================================
#  Set up logger
# ==============================================================================

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler(lg.log_file_name)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

# ==============================================================================
#  Basins function
# ==============================================================================
#
# Retrieves upstream subcatchments of an outlet point.
#
# ==============================================================================

debug_mode = False

#  Functions to aupport all subbasin finding methods


def get_subbasin(damFeat, hybasLevel):
    """Get hydrobasin subbasin (at level hybasLevel) dam is located in"""
    damFeat = ee.Feature(damFeat)
    outlet_point = damFeat.geometry()

    hydrobasins = ee.FeatureCollection(dta.hydrosheds_dict.get(hybasLevel))
    outlet_subcatch = hydrobasins.filterBounds(outlet_point)

    hybas_id = ee.Number(ee.Feature(outlet_subcatch.first()).get("HYBAS_ID"))
    pfaf_id = ee.Number(ee.Feature(outlet_subcatch.first()).get("PFAF_ID"))
    spfaf_id = ee.Number(pfaf_id).format("%s")

    dict = ee.Dictionary(
        {"PFAF_ID": pfaf_id, "SPFAF_ID": spfaf_id, "HYBAS_ID": hybas_id}
    )

    return dict


def get_parents(children, subcatchments):
    """Given a hydrobasin subbasin and set of subbbasins to search within
    generate a list of direct parent sub-basins
    """
    parent_list = ee.List(children).map(
        lambda child: (
            ee.FeatureCollection(subcatchments)
            .filter(ee.Filter.eq("NEXT_DOWN", child))
            .aggregate_array("HYBAS_ID")
        )
    )

    distinct_parents = ee.List(parent_list).flatten().distinct()

    return distinct_parents


def find_hybas_bounding_level(damFeat):
    """Given a dam location, find the highest hydrobasins level which contains
    a subbasin that completely encloses the dam catchment
    """
    damFeat = ee.Feature(damFeat)
    dam_point = damFeat.geometry()

    def algorithm(current, previous):

        previous = ee.List(previous)

        level = ee.Number.format(previous.length())
        hydrosheds = dta.hydrosheds_dict.get(level)

        outlet_subcatch = ee.FeatureCollection(hydrosheds).filterBounds(dam_point)
        outlet_subcatch_id = ee.Number(
            ee.Feature(outlet_subcatch.first()).get("HYBAS_ID")
        )

        ancestors = get_parents(ee.List([outlet_subcatch_id]), hydrosheds)
        ancestor_count = ee.Number(ee.List(ancestors).length())

        returnValue = ee.Algorithms.If(
            ancestor_count.eq(0), ee.List([previous.length()]), ee.List([])
        )

        return previous.add(returnValue)

    start = ee.List([[1]])
    indicesList = ee.List.sequence(0, 11, 1)
    refLevel = indicesList.iterate(algorithm, start)

    distinct_levels = ee.List(refLevel).flatten()

    bounding_level = ee.Number(ee.List(distinct_levels).get(-1)).format("%s")

    return bounding_level


#  Functions for subbasin finding method 1 (trace ancestors)


def get_ancestors(id, subcatchments):
    """Given a hydrobasins (12) subbasin id and set of hydrobasins (12) subbasins to
    search, trace upstream basins by following the NEXT_DOWN field. Should work
    with any hydrobasins dataset provided id and subbasin parameters are from the
    same level.

    While loops are not supported by EE, so we cannot specify a stopping condition
    (id not among NEXT_DOWNS). To keep all computation server-side we set the number of
    iterations to the number of sub-catchments to search less the number of
    source subbasins (no upstean) and empty results are filtered out.
    """

    start_list = ee.List([]).add(ee.List([id]))

    if debug_mode == True:
        print("[DEBUG]\n [get_ancestors] Start list: " + start_list.getInfo())
        print(
            "[DEBUG]\n [get_ancestors] Subcatchments size: "
            + subcatchments.size().getInfo()
        )

    nodes = ee.List(subcatchments.aggregate_array("HYBAS_ID")).distinct()
    next_nodes = ee.List(subcatchments.aggregate_array("NEXT_DOWN")).distinct()

    sources = ee.Number(
        ee.List(nodes)
        .filter(ee.Filter.inList("item", ee.List(next_nodes)).Not())
        .length()
    )

    maxIter = subcatchments.size().add(1).subtract(sources)
    indicesList = ee.List.sequence(0, maxIter.subtract(1), 1)

    if debug_mode == True:
        print("[DEBUG]\n [get_ancestors] maxIter: " + maxIter.getInfo())

    def algorithm(current, previous):

        child_list = ee.List(previous).get(-1)
        parent_list = ee.List(child_list).map(
            lambda child: (
                subcatchments.filter(ee.Filter.eq("NEXT_DOWN", child)).aggregate_array(
                    "HYBAS_ID"
                )
            )
        )

        distinct_parents = ee.List(parent_list).flatten().distinct()

        return ee.List(previous).add(distinct_parents)

    ancestors = indicesList.iterate(algorithm, start_list)
    distinct_ancestors = ee.List(ancestors).flatten().distinct().slice(1, None, 1)

    return distinct_ancestors


#  Functions for subbasin finding method 2 (heuristic)
#  N/A

# Functions for subbasin finding method 3


def all_odd_or_zero(digit_string):
    """Check if trailing digits are all odd or zero"""
    oddMatches = ee.String(digit_string).match("^\d*[013579]$")
    all_odd_or_zero = ee.Number(ee.Algorithms.If(oddMatches.length().neq(0), 1, 0))

    if debug_mode == True:
        print("[DEBUG]\n [all_odd_or_zero] - oddMatches", oddMatches.length())

    return all_odd_or_zero


def get_trailA(A, B):
    """Get trailing digits for pfafstetter id A"""
    A = ee.String(A)
    B = ee.String(B)

    def algorithm(current, previous):
        previous = ee.List(previous)
        k = ee.Number(previous.length())

        sA = ee.String(A).slice(0, k)
        rA = ee.String("^").cat(sA)
        mB = ee.Number(ee.String(B).match(rA).length())

        returnValue = ee.Algorithms.If(mB.gt(0), ee.List([k]), ee.List([]))
        return previous.add(returnValue)

    start = ee.List([[A, B]])
    indicesList = ee.List.sequence(0, 11, 1)
    lcs_nested_list = indicesList.iterate(algorithm, start)

    lcs_list = ee.List(lcs_nested_list).flatten()
    n = ee.Number(ee.List(lcs_list).get(-1))
    trailA = ee.String(A).slice(n, None)

    if debug_mode == True:
        print("[DEBUG]\n [get_trailA] - lcs_nested_list", lcs_nested_list)
        print("[DEBUG]\n [get_trailA] - lcs_list", lcs_list)
        print("[DEBUG]\n [get_trailA] n: " + n.getInfo())

    return trailA


def batch_find_upstream_basins(dams_ftc, c_dam_ids):

    for c_dam_id in c_dam_ids:

        c_dam_id_str = str(c_dam_id)
        dam_id = ee.Number(c_dam_id)

        damFeat = dams_ftc.filter(ee.Filter.eq("id", dam_id)).first()

        if debug_mode == True:
            print("[batch_find_upstream_basins]", damFeat.getInfo())

        # ==================================================================
        # Export Location
        # ==================================================================

        if cfg.exportRawDamPts == True:
            msg = """Exporting raw dam location"""
            try:
                logger.info("{msg} {c_dam_id_str}")

                ftc = ee.FeatureCollection(ee.Feature(damFeat))
                selected_properties = ee.List(["country", "name", "id"])

                location_ftc = ftc.map(
                    lambda feat: ee.Feature(feat).select(selected_properties)
                )

            except Exception as error:
                logger.exception(f"{msg} {c_dam_id_str}")
                continue

        # ==================================================================
        # Snap Location
        # ==================================================================

        try:
            snappedDamFeat = heet_snap.jensen_snap_hydroriver(damFeat)
            logger.info(f"Snapping Dam Location {c_dam_id_str}")

        except Exception as error:
            print(error, c_dam_id_str)
            mtr.active_analyses.remove(int(c_dam_id_str))
            continue

        # ==================================================================
        # Find upstream sub-basins
        # ==================================================================

        try:
            # Find the highest hydrobasin level that completely encloses the
            # catchment
            logger.info(
                "Finding the highest Hydrobasins level that encloses the catchment"
            )

            hybas_bounding_level = find_hybas_bounding_level(damFeat)
            outlet_pt_sbasin_bl = get_subbasin(snappedDamFeat, hybas_bounding_level)
            opt_bl_spfafid = outlet_pt_sbasin_bl.get("SPFAF_ID")

        except Exception as error:
            logger.exception(
                "Finding highest hydrobasin level and bounding basin that encloses the catchment"
            )
            continue

        try:
            # Find the hydrobasins level 12 subbasin the dam is in
            logger.info("Finding the hydrobasins level 12 sub-basin of the dam")

            outlet_pt_sbasin_12 = get_subbasin(snappedDamFeat, "12")

            opt_12_hybasid = outlet_pt_sbasin_12.get("HYBAS_ID")
            opt_12_pfafid = outlet_pt_sbasin_12.get("PFAF_ID")

            dam_subbasin_feat = dta.HYDROBASINS12.filter(
                ee.Filter.eq("HYBAS_ID", opt_12_hybasid)
            )

        except Exception as error:
            logger.info("Finding Highest Hydrobasins level that encloses the catchment")

        try:
            # Remove (filter out) subbasins that cannot be upstream of the dam
            # from hydrobasins 12 to limit search space
            logger.info(
                "Removing downstream sub-basins and those outside the bounding basin from search"
            )

            SHYDROBASINS12 = (
                dta.HYDROBASINS12
                # Remove subbasins with a pfafsetter id greater than that of the
                # level 12 subbasin dam is in
                .filter(ee.Filter.gt("PFAF_ID", opt_12_pfafid))
                # Restrict seach to shared top-level basin
                .filter(ee.Filter.stringStartsWith("SPFAF_ID", opt_bl_spfafid)).sort(
                    "SORT", True
                )
            )

        except Exception as error:
            logger.exception(
                "Removing downstream sub-basins and those outside the bounding basin from search"
            )

        if cfg.upstreamMethod == 1:
            try:
                logger.info("Finding upstream sub-basins by tracing ancestors")
                upstream_subbasins_list = get_ancestors(opt_12_hybasid, SHYDROBASINS12)
            except Exception as error:
                logger.exception(" Finding upstream sub-basins by tracing ancestors")
                continue

        if cfg.upstreamMethod == 2:
            try:
                logger.info("Heuristics - remove downstream sub-basins")
                upstream_subbasins_list = ee.List(
                    SHYDROBASINS12.aggregate_array("HYBAS_ID")
                )
            except Exception as error:
                logger.exception("Heuristics - remove downstream sub-basins")
                continue

        if cfg.upstreamMethod == 3:

            def tag_upstream(feat):
                A = outlet_pt_sbasin_12.get("SPFAF_ID")
                B = feat.get("SPFAF_ID")

                trailA = get_trailA(A, B)
                allOddOrZero = all_odd_or_zero(trailA)

                feat = feat.set({"TRAIL_A": ee.String(trailA)})
                feat = feat.set({"ALL_ODD_OR_ZERO": ee.Number(allOddOrZero)})

                return feat

            try:
                logger.info("Identifying upstream sub-basins from pfafstetter ids")
                SHYDROBASINS12 = SHYDROBASINS12.map(tag_upstream)
                UPSTREAM = SHYDROBASINS12.filter(
                    ee.Filter.eq("ALL_ODD_OR_ZERO", ee.Number(1))
                )

                upstream_subbasins_list = ee.List(UPSTREAM.aggregate_array("HYBAS_ID"))

            except Exception as error:
                logger.exception(
                    "[ERROR] Identifying upstream sub-basins from pfafstetter ids"
                )
                continue

        snappedDamFeat = snappedDamFeat.set("outlet_subcatch_id", opt_12_hybasid)
        snappedDamFeat = snappedDamFeat.set(
            "ancestor_ids", ee.String.encodeJSON(upstream_subbasins_list)
        )

        if cfg.exportSnappedDamPts == True:
            msg = """Exporting snapped dam location"""
            try:
                logger.info(f"{msg} {c_dam_id_str}")

                ftc = ee.FeatureCollection(ee.Feature(snappedDamFeat))

                location_ftc = ftc.map(lambda feat: ee.Feature(feat))

                heet_export.export_ftc(
                    location_ftc, c_dam_id_str, "snapped_dam_location"
                )
            except Exception as error:
                logger.exception(f"{msg} {c_dam_id_str}")
                continue

        if debug_mode == True:
            print(
                "[batch_find_upstream_basins] snappedDamFeat", snappedDamFeat.getInfo()
            )


if __name__ == "__main__":

    # Development
    print("Development Run...")
    dams_ftc = ee.FeatureCollection(
        "users/kkh451/XHEET/GAWLAN_20230126-1434/user_inputs"
    )
    c_dam_ids = [1201]
    debug_mode = True
    print(debug_mode)
    batch_find_upstream_basins(dams_ftc, c_dam_ids)
