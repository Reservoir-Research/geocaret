""" """
import ee
import logging

import_exceptions = (ModuleNotFoundError, ee.ee_exception.EEException)
try:
    from geocaret import config as cfg
    from geocaret import data as dta
    from geocaret import export
    from geocaret import reservoir as res
    from geocaret import monitor as mtr
    from geocaret import snap as snap
    from geocaret import log as lg

except import_exceptions:
    if not ee.data._credentials:
        ee.Initialize()

    import geocaret.config as cfg
    import geocaret.data as dta
    import geocaret.export
    import geocaret.reservoir as res
    import geocaret.monitor as mtr
    import geocaret.snap as snap
    import geocaret.log as lg
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
# Utils
# ==============================================================================


def filter_main(hyriv_id, hydrorivers_extract):

    hydrorivers_extract = ee.FeatureCollection(hydrorivers_extract)

    # Heuristics
    # print("[DEBUG] [filter_main] hyriv_id", hyriv_id.getInfo())

    # Extract mean discharge at dam site.
    main_dam_reach_ft = hydrorivers_extract.filter(ee.Filter.eq("HYRIV_ID", hyriv_id))

    # print("[DEBUG] [filter_main] feat", main_dam_reach_ft.getInfo())

    dam_ord_clas = main_dam_reach_ft.first().get("ORD_CLAS")

    # print("[DEBUG] [filter_main] River Clas", dam_ord_clas.getInfo())

    # Filter out reaches not same order class
    main_hydrorivers = hydrorivers_extract.filter(
        ee.Filter.eq("ORD_CLAS", dam_ord_clas)
    )

    return main_hydrorivers


def find_main_channel(inundated_river_ftc, damFeat):
    # Find main river channel

    main_dam_reach_ft = (
        inundated_river_ftc.filterBounds(damFeat.geometry())
        .sort("DIS_AV_CMS", False)
        .first()
    )

    main_dam_reach_id = main_dam_reach_ft.get("HYRIV_ID")

    inundated_river_main_ftc = filter_main(main_dam_reach_id, inundated_river_ftc)

    if debug_mode == True:
        print(" [delineate_river] damFeat", damFeat.getInfo(), "\n")
        print(
            " [delineate_river] inundated_river_ftc",
            inundated_river_ftc.getInfo(),
            "\n",
        )
        print(" [delineate_river] main_dam_reach_ft", main_dam_reach_ft.getInfo(), "\n")
        print(" [delineate_river] main_dam_reach_id", main_dam_reach_id.getInfo(), "\n")
        print(
            " [delineate_river] inundated_river_ftc",
            inundated_river_main_ftc.getInfo(),
            "\n",
        )

    return inundated_river_main_ftc


# Generic Function to remove a property from a feature
def remove_property(feat, property_name):

    properties = feat.propertyNames()
    selected_properties = properties.filter(ee.Filter.neq("item", property_name))

    return feat.select(selected_properties)


def polygon_to_lines(poly_ftc):

    # print(" [polygon_to_lines] Input Polygon FTC", poly_ftc.getInfo(),"\n")

    # Convert polygon to a collection of points
    poly_points_list = poly_ftc.first().geometry().coordinates().get(0)
    # print(" [polygon_to_lines] Polygon Points List", poly_points_list.getInfo(),"\n")

    # Divide collection of points into start and end pts of boundary lines
    # Start points are all pts starting at 0 (1st pt).
    # End points are all pts starting at 1 (2nd pt) with the first start pt
    # being the final end pt.

    poly_start_pts_list = ee.List(poly_points_list).slice(0, None, 1)
    poly_end_pts_list = (
        ee.List(poly_points_list).slice(1, None, 1)
        # Changed from -1 (last pt) to 0
        .add(ee.List(poly_points_list).get(0))
    )

    poly_line_pts_list = poly_start_pts_list.zip(poly_end_pts_list)

    # print(" [polygon_to_lines] Polygon Start Points List", poly_start_pts_list.getInfo(),"\n")
    # print(" [polygon_to_lines] Polygon End Points List", poly_end_pts_list.getInfo(),"\n")
    # print(" [polygon_to_lines] Polygon Line Coords List", poly_line_pts_list.getInfo(),"\n")

    poly_boundaries_ftc = ee.FeatureCollection(
        poly_line_pts_list.map(snap.pts_to_linestring)
    )

    poly_boundaries_ftc = poly_boundaries_ftc.map(
        lambda rfeat: remove_property(rfeat, "pt_start")
    )
    poly_boundaries_ftc = poly_boundaries_ftc.map(
        lambda rfeat: remove_property(rfeat, "pt_end")
    )

    # print("Polygon Boundary Lines FTC", poly_boundaries_ftc.getInfo(),"\n")
    return poly_boundaries_ftc


def inundated_reaches(sres_ftc):

    # Reaches that intersect with (or are fully contained) by reservoir
    reaches_sres_ftc = dta.HYDRORIVERS.filterBounds(sres_ftc.geometry())

    def is_source(rfeat):

        # Source (Not in NEXT_DOWN set)
        t_hyriv_id = rfeat.get("HYRIV_ID")

        is_source = ee.Algorithms.If(
            # If hyriv_id is not in next_down, must be source
            ee.List(next_down_set).contains(t_hyriv_id),
            0,
            1,
        )

        rfeat = rfeat.set("is_source", is_source)

        return rfeat

    def is_sink(rfeat):

        # Sink (NEXT_DOWN not in HYRIV_ID Set)
        t_next_down = rfeat.get("NEXT_DOWN")

        is_sink = ee.Algorithms.If(
            # If next_down is not in hyriv_id, must be sink
            ee.List(hyriv_id_set).contains(t_next_down),
            0,
            1,
        )

        rfeat = rfeat.set("is_sink", is_sink)

        return rfeat

    # Tag inlets/outlets that are Source or Sink Reaches
    hyriv_id_set = reaches_sres_ftc.aggregate_array("HYRIV_ID")
    next_down_set = reaches_sres_ftc.aggregate_array("NEXT_DOWN")

    reaches_sres_ftc = reaches_sres_ftc.map(is_source)
    reaches_sres_ftc = reaches_sres_ftc.map(is_sink)

    return reaches_sres_ftc


def delineate_river(damFeat, res_ftc, c_dam_id_str):

    if debug_mode == True:
        global cDamFeat

        global inundated_river_source_ftc
        global inundated_river_sink_ftc
        global inundated_river_other_ftc
        global inundated_river_cftc
        global inundated_river_ftc

        global sres_ftc
        global sres_boundaries_ftc

        global reaches_sres_ftc
        global reaches_sres_iolet_sas_ftc
        global reaches_sres_iolet_source_ftc
        global reaches_sres_iolet_sink_ftc
        global reaches_sres_iolet_other_ftc

        global main_dam_reach_ft
        global main_dam_reach_id

        global main_channel_ids
        global inundated_river_main_ftc

    cDamFeat = damFeat
    # Simplify reservoir vector to single outer boundary
    sres_ftc = res.simplify_reservoir(res_ftc, c_dam_id_str)

    # Convert simplified reservoir to a collection of boundary lines
    sres_boundaries_ftc = polygon_to_lines(sres_ftc)

    # ==========================================================================
    # Export simplified reservoir line boundary
    # ==========================================================================

    if cfg.exportSimplifiedReservoirBoundary == True:
        msg = "Exporting simplified reservoir boundary"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(
                sres_boundaries_ftc, c_dam_id_str, "simple_reservoir_boundary"
            )

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    # Using the simplified reservoir and boundary lines
    # Identify inundated river reaches (river reaches that cross or are
    # enclosed by the reservoir boundary)

    reaches_sres_ftc = inundated_reaches(sres_ftc)
    if debug_mode == True:
        print(
            "[DEBUG] [delineate_river] reaches_sres_ftc",
            reaches_sres_ftc.getInfo(),
            "\n",
        )

    # ! IMPORTANT
    # This code removes river reaches that are unlikely to be main river
    # and reduces the computational cost of trimming source and sink reaches.
    # (this is only appropriate if only main river channel is desired)
    if cfg.exportRiver == False:
        reaches_sres_ftc = find_main_channel(reaches_sres_ftc, damFeat)

    # Categorise inundated reaches.
    # Crosses reservoir boundary
    # - Source (upsteam start point)
    # - Sink (downsteam end point)
    # - Other (neither source nor sink)

    # River reaches inside simplified reservoir

    def has_boundary_pts(rfeat):

        boundary_pts = sres_boundaries_ftc.toList(1000000).map(
            lambda res_geom: ee.Algorithms.If(
                # Intersects
                ee.Feature(res_geom).intersects(rfeat, ee.ErrorMargin(1)),
                # Intersection
                ee.Feature(res_geom).intersection(rfeat, ee.ErrorMargin(1)),
                999,
            )
        )

        nbpts = ee.List(boundary_pts).filter(ee.Filter.neq("item", 999)).length()
        rfeat = rfeat.set("nbpts", nbpts)
        return rfeat

    reaches_sres_sas_ftc = (
        reaches_sres_ftc.filter(ee.Filter.eq("is_source", 1)).filter(
            ee.Filter.eq("is_sink", 1)
        )
    ).map(has_boundary_pts)

    reaches_sres_source_ftc = (
        reaches_sres_ftc.filter(ee.Filter.eq("is_source", 1)).filter(
            ee.Filter.eq("is_sink", 0)
        )
    ).map(has_boundary_pts)

    reaches_sres_sink_ftc = (
        reaches_sres_ftc.filter(ee.Filter.eq("is_source", 0)).filter(
            ee.Filter.eq("is_sink", 1)
        )
    ).map(has_boundary_pts)

    reaches_sres_other_ftc = (
        reaches_sres_ftc.filter(ee.Filter.eq("is_source", 0)).filter(
            ee.Filter.eq("is_sink", 0)
        )
    ).map(lambda rfeat: rfeat.set("nbpts", -999))

    reaches_sres_iolet_ftc = ee.FeatureCollection(
        ee.List(
            [
                reaches_sres_sas_ftc,
                reaches_sres_source_ftc,
                reaches_sres_sink_ftc,
                reaches_sres_other_ftc,
            ]
        )
    ).flatten()

    if debug_mode == True:
        print(
            "[DEBUG] [delineate_river] reaches_sres_iolet_ftc",
            reaches_sres_iolet_ftc.getInfo(),
            "\n",
        )

    # Simple terminal reaches
    reaches_sres_iolet_ssas_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 1))
        .filter(ee.Filter.eq("is_sink", 1))
        .filter(ee.Filter.eq("nbpts", 1))
    )

    reaches_sres_iolet_ssource_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 1))
        .filter(ee.Filter.eq("is_sink", 0))
        .filter(ee.Filter.eq("nbpts", 1))
    )

    reaches_sres_iolet_ssink_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 0))
        .filter(ee.Filter.eq("is_sink", 1))
        .filter(ee.Filter.eq("nbpts", 1))
    )

    # Complex terminal reaches
    reaches_sres_iolet_csas_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 1))
        .filter(ee.Filter.eq("is_sink", 1))
        .filter(ee.Filter.greaterThanOrEquals("nbpts", 2))
    )

    reaches_sres_iolet_csource_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 1))
        .filter(ee.Filter.eq("is_sink", 0))
        .filter(ee.Filter.greaterThanOrEquals("nbpts", 2))
    )

    reaches_sres_iolet_csink_ftc = (
        reaches_sres_iolet_ftc.filter(ee.Filter.eq("is_source", 0))
        .filter(ee.Filter.eq("is_sink", 1))
        .filter(ee.Filter.greaterThanOrEquals("nbpts", 2))
    )

    inundated_river_other_ftc = reaches_sres_iolet_ftc.filter(
        ee.Filter.eq("is_source", 0)
    ).filter(ee.Filter.eq("is_sink", 0))

    if debug_mode == True:
        print(
            "[DEBUG] [delineate_river] ssas",
            reaches_sres_iolet_ssas_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] ssource",
            reaches_sres_iolet_ssource_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] ssink",
            reaches_sres_iolet_ssink_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] csas",
            reaches_sres_iolet_csas_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] csource",
            reaches_sres_iolet_csource_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] csink",
            reaches_sres_iolet_csink_ftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG] [delineate_river] other", inundated_river_other_ftc.getInfo(), "\n"
        )

    # ==========================================================================
    # UTIL FUNCTIONS WITHIN DELINEATE RIVER
    # ==========================================================================

    def reach_to_lines_source_ftc(rfeat):

        # ======================================================================
        # Reaches to lines
        # ======================================================================

        rfeat = ee.Feature(rfeat)

        # Convert Reach Multigeoms to List of Pt Coordinates
        reach_points_list = rfeat.geometry().coordinates()

        # Convert Coordinate List to List of Start and End Points of Lines
        # (Assumes points in connecting order)
        reach_start_points_list = ee.List(reach_points_list).slice(0, -1, 1)
        reach_end_points_list = ee.List(reach_points_list).slice(1, None, 1)
        reach_line_pts_list = reach_start_points_list.zip(reach_end_points_list)

        # Decompose the river reach pts (can be multiple lines) into constituent line sections
        # (reach lines); Convert Start and End Points to LineString FTC
        reach_lines_ftc = ee.FeatureCollection(
            reach_line_pts_list.map(snap.pts_to_linestring)
        )

        def is_iolet(geom_line):

            has_iolet = sres_boundaries_ftc.toList(1000000).map(
                lambda res_geom: ee.Algorithms.If(
                    ee.Feature(res_geom).intersects(geom_line, ee.ErrorMargin(1)), 1, 0
                )
            )

            intersects = has_iolet.distinct().sort().reverse().get(0)
            geom_line = geom_line.set("iolet", ee.Number(intersects))

            return geom_line

        def has_boundary_pts(geom_line):

            boundary_pts = sres_boundaries_ftc.toList(1000000).map(
                lambda res_geom: ee.Algorithms.If(
                    # Intersects
                    ee.Feature(res_geom).intersects(geom_line, ee.ErrorMargin(1)),
                    # Intersection
                    ee.Feature(res_geom).intersection(geom_line, ee.ErrorMargin(1)),
                    999,
                )
            )

            boundary_pts = ee.List(boundary_pts).filter(ee.Filter.neq("item", 999))
            geom_line = geom_line.set("boundary_pts", boundary_pts)

            return geom_line

        # Determine which of the line sections crosses the reservoir boundary
        # Tag iolet line segments (cross the reservoir boundary)
        lines_iolet_ftc = reach_lines_ftc.map(is_iolet)

        # Identify point where line sections cross the reservoir boundary
        lines_iolet_ftc = lines_iolet_ftc.map(has_boundary_pts)

        if debug_mode == True:
            print("[reach_to_lines_ftc] River Feature", rfeat.getInfo(), "\n")
            print(
                "[reach_to_lines_ftc] Reach Points List",
                reach_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach Start Points List",
                reach_start_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach End Points List",
                reach_end_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach Line Coords List",
                reach_line_pts_list.getInfo(),
                "\n",
            )
            print(" [reach_to_lines_ftc] Reach Lines", reach_lines_ftc.getInfo(), "\n")

        # ======================================================================
        # Truncate lines within source/sink reaches
        # ======================================================================
        def truncate_source_line(lines_iolet_ftc):

            # Identify Line Segments Outside Reservoir to Discard
            lines_iolet_list = lines_iolet_ftc.toList(1000000)
            iolet_list = lines_iolet_ftc.aggregate_array("iolet")
            retain_from_index = ee.List(iolet_list).indexOf(1)

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_source_line] lines_iolet_list",
                    lines_iolet_list.getInfo(),
                    "\n",
                )
                print(
                    "[DEBUG] [truncate_source_line] iolet_list",
                    iolet_list.getInfo(),
                    "\n",
                )
                print(
                    "[DEBUG] [truncate_source_line]", retain_from_index.getInfo(), "\n"
                )

            # Identify the line Segment that Needs to be Trimmed
            line_to_trim_ft = ee.Feature(
                lines_iolet_list.slice(
                    retain_from_index, ee.Number(retain_from_index).add(1), 1
                ).get(0)
            )

            # Identify the line segment downstream of the one that needs to be
            # trimmed
            selected_lines_list = lines_iolet_list.slice(
                ee.Number(retain_from_index).add(1), None, 1
            )

            ##print(" [truncate_source_reach] Retain From Index", retain_from_index)
            ##print(" [truncate_source_reach] Line to Trim", line_to_trim_ft)

            # Trim iolet line segment (cut at boundary pt closest to upstream pt in
            # case line segment crosses reservoir boundary more than once.

            pt_start = line_to_trim_ft.get("pt_start")
            pt_end = line_to_trim_ft.get("pt_end")

            def upstream_dist(bpt):
                dist = ee.Feature(bpt).distance(pt_start)
                bpt = ee.Feature(bpt).set("updist", dist)
                return bpt

            boundary_pts = line_to_trim_ft.get("boundary_pts")
            boundary_pts_ftc = ee.FeatureCollection(
                ee.List(boundary_pts).map(upstream_dist)
            )

            boundary_pts_filtered_ftc = (
                boundary_pts_ftc
                # Occasional infinite values; tol of 1e10 to remove
                .filter(ee.Filter.lte("updist", 1e10)).sort("updist", True)
            )

            npt_start = (
                ee.FeatureCollection(boundary_pts_filtered_ftc).first().geometry()
            )

            if debug_mode == True:
                print(
                    " [truncate_source_reach] Boundary Pts", boundary_pts_ftc.getInfo()
                )
                print(
                    " [truncate_source_reach] Filtered Boundary Pts",
                    boundary_pts_filtered_ftc.getInfo(),
                )
                print(
                    " [truncate_source_reach] In Points",
                    npt_start.getInfo(),
                    pt_end.getInfo(),
                )

            # TODO temp ntp_start- pt_start
            trimmed_line_geom_source = ee.Geometry.LineString(
                ee.List([npt_start, pt_end])
            )

            trimmed_line_geom = trimmed_line_geom_source

            # Update the line segment feature with the new geometry
            line_to_trim_ft = line_to_trim_ft.setGeometry(trimmed_line_geom)

            # Combined the trimmed segment with other line segments we want to keep
            trimmed_line_ftc = ee.FeatureCollection(ee.Feature(line_to_trim_ft))
            selected_lines_ftc = ee.FeatureCollection(selected_lines_list)

            if debug_mode == True:
                print(
                    " [truncate_source_reach] Trimmed Source Line",
                    trimmed_line_ftc.getInfo(),
                    "\n",
                )
                print(
                    " [truncate_source_reach] Selected Source Lines List",
                    selected_lines_list.getInfo(),
                    "\n",
                )
                print(
                    " [truncate_source_reach] Selected Source Lines FTC",
                    selected_lines_ftc.getInfo(),
                    "\n",
                )

            out_ftc = ee.Algorithms.If(
                selected_lines_ftc.size().eq(0),
                trimmed_line_ftc,
                trimmed_line_ftc.merge(selected_lines_ftc).union(),
            )

            outgeom = ee.FeatureCollection(out_ftc).first().geometry()

            return outgeom

        # Both routes visible in debug mode
        outgeom = truncate_source_line(lines_iolet_ftc)
        rfeat = rfeat.setGeometry(outgeom)

        if debug_mode == True:
            print("[DEBUG][reach_to_lines_ftc] Reach Feature", rfeat.getInfo(), "\n")

        return rfeat

    def reach_to_lines_sink_ftc(rfeat):

        # ======================================================================
        # Reaches to lines
        # ======================================================================

        rfeat = ee.Feature(rfeat)

        # Convert Reach Multigeoms to List of Pt Coordinates
        reach_points_list = rfeat.geometry().coordinates()

        # Convert Coordinate List to List of Start and End Points of Lines
        # (Assumes points in connecting order)
        reach_start_points_list = ee.List(reach_points_list).slice(0, -1, 1)
        reach_end_points_list = ee.List(reach_points_list).slice(1, None, 1)
        reach_line_pts_list = reach_start_points_list.zip(reach_end_points_list)

        # Decompose the river reach pts (can be multiple lines) into constituent line sections
        # (reach lines); Convert Start and End Points to LineString FTC
        reach_lines_ftc = ee.FeatureCollection(
            reach_line_pts_list.map(snap.pts_to_linestring)
        )

        def is_iolet(geom_line):

            has_iolet = sres_boundaries_ftc.toList(1000000).map(
                lambda res_geom: ee.Algorithms.If(
                    ee.Feature(res_geom).intersects(geom_line, ee.ErrorMargin(1)), 1, 0
                )
            )

            intersects = has_iolet.distinct().sort().reverse().get(0)
            geom_line = geom_line.set("iolet", ee.Number(intersects))

            return geom_line

        def has_boundary_pts(geom_line):

            boundary_pts = sres_boundaries_ftc.toList(1000000).map(
                lambda res_geom: ee.Algorithms.If(
                    # Intersects
                    ee.Feature(res_geom).intersects(geom_line, ee.ErrorMargin(1)),
                    # Intersection
                    ee.Feature(res_geom).intersection(geom_line, ee.ErrorMargin(1)),
                    999,
                )
            )

            boundary_pts = ee.List(boundary_pts).filter(ee.Filter.neq("item", 999))
            geom_line = geom_line.set("boundary_pts", boundary_pts)

            return geom_line

        # Determine which of the line sections crosses the reservoir boundary
        # Tag iolet line segments (cross the reservoir boundary)
        lines_iolet_ftc = reach_lines_ftc.map(is_iolet)

        # Identify point where line sections cross the reservoir boundary
        lines_iolet_ftc = lines_iolet_ftc.map(has_boundary_pts)

        if debug_mode == True:
            print("[reach_to_lines_ftc] River Feature", rfeat.getInfo(), "\n")
            print(
                "[reach_to_lines_ftc] Reach Points List",
                reach_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach Start Points List",
                reach_start_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach End Points List",
                reach_end_points_list.getInfo(),
                "\n",
            )
            print(
                "[reach_to_lines_ftc] Reach Line Coords List",
                reach_line_pts_list.getInfo(),
                "\n",
            )
            print(" [reach_to_lines_ftc] Reach Lines", reach_lines_ftc.getInfo(), "\n")

        # ======================================================================
        # Truncate lines within source/sink reaches
        # ======================================================================

        def truncate_sink_line(lines_iolet_ftc):

            # Identify Line Segments Outside Reservoir to Discard
            lines_iolet_list = lines_iolet_ftc.toList(1000000)
            iolet_list = lines_iolet_ftc.aggregate_array("iolet")

            retain_to_index = ee.List(iolet_list).lastIndexOfSubList(ee.List([1]))

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] lines_iolet_list",
                    lines_iolet_list.getInfo(),
                    "\n",
                )
                print(
                    "[DEBUG] [truncate_sink_line] iolet_list",
                    iolet_list.getInfo(),
                    "\n",
                )
                print("[DEBUG] [truncate_sink_line]", retain_to_index.getInfo(), "\n")

            # Identify the Line Segment that Needs to be Trimmed
            line_to_trim_ft = ee.Feature(
                lines_iolet_list.slice(0, ee.Number(retain_to_index).add(1), 1).get(-1)
            )

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] line_to_trim_ft",
                    line_to_trim_ft.getInfo(),
                    "\n",
                )

            # Identify line segments upstream of the one to be trimmed
            # (to be kept)
            selected_lines_list = lines_iolet_list.slice(
                0, ee.Number(retain_to_index), 1
            )

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] selected_lines_list",
                    selected_lines_list.getInfo(),
                    "\n",
                )

            # Trim iolet line segment (cut at boundary pt closest to upstream pt in
            # case line segment crosses reservoir boundary more than once.

            pt_start = line_to_trim_ft.get("pt_start")
            pt_end = line_to_trim_ft.get("pt_end")

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] pt_start, pt_end, ",
                    pt_start.getInfo(),
                    pt_end.getInfo(),
                    "\n",
                )

            def upstream_dist(bpt):
                dist = ee.Feature(bpt).distance(pt_start)
                bpt = ee.Feature(bpt).set("updist", dist)
                return bpt

            boundary_pts = line_to_trim_ft.get("boundary_pts")
            boundary_pts_ftc = ee.FeatureCollection(
                ee.List(boundary_pts).map(upstream_dist)
            )

            boundary_pts_filtered_ftc = (
                boundary_pts_ftc
                # Occasional infinite values; tol of 1e10 to remove
                .filter(ee.Filter.lte("updist", 1e10)).sort("updist", False)
            )

            npt_end = ee.FeatureCollection(boundary_pts_filtered_ftc).first().geometry()

            if debug_mode == True:
                print(" [truncate_sink_reach] Boundary Pts", boundary_pts_ftc.getInfo())
                print(
                    " [truncate_sink_reach] Filtered Boundary Pts",
                    boundary_pts_filtered_ftc.getInfo(),
                )
                print(
                    " [truncate_sink_reach] In Points",
                    pt_start.getInfo(),
                    npt_end.getInfo(),
                )

            trimmed_line_geom_sink = ee.Geometry.LineString(
                ee.List([pt_start, npt_end])
            )

            trimmed_line_geom = trimmed_line_geom_sink

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] trimmed_line_geom",
                    trimmed_line_geom.getInfo(),
                    "\n",
                )

            # Update the line segment feature with the new geometry
            line_to_trim_ft = line_to_trim_ft.setGeometry(trimmed_line_geom)

            if debug_mode == True:
                print(
                    "[DEBUG] [truncate_sink_line] line_to_trim_ft",
                    line_to_trim_ft.getInfo(),
                    "\n",
                )

            # Combined the trimmed segment with other line segments we want to keep
            trimmed_line_ftc = ee.FeatureCollection(ee.Feature(line_to_trim_ft))
            selected_lines_ftc = ee.FeatureCollection(selected_lines_list)

            out_ftc = ee.Algorithms.If(
                selected_lines_ftc.size().eq(0),
                trimmed_line_ftc,
                trimmed_line_ftc.merge(selected_lines_ftc).union(),
            )

            outgeom = ee.FeatureCollection(out_ftc).first().geometry()

            return outgeom

        # Both routes visible in debug mode
        outgeom = truncate_sink_line(lines_iolet_ftc)
        rfeat = rfeat.setGeometry(outgeom)

        if debug_mode == True:
            print("[DEBUG][reach_to_lines_ftc] Reach Feature", rfeat.getInfo(), "\n")

        return rfeat

    # ==========================================================================
    # END - UTIL FUNCTIONS WITHIN DELINEATE RIVER
    # ==========================================================================

    # ==========================================================================
    # [0] Process simple terminal reaches
    # ==========================================================================
    sres_geom = sres_ftc.geometry()

    inundated_river_ssas_ftc = reaches_sres_iolet_ssas_ftc.map(
        lambda rfeat: ee.Feature(rfeat).intersection(sres_geom)
    )

    inundated_river_ssink_ftc = reaches_sres_iolet_ssink_ftc.map(
        lambda rfeat: ee.Feature(rfeat).intersection(sres_geom)
    )

    inundated_river_ssource_ftc = reaches_sres_iolet_ssource_ftc.map(
        lambda rfeat: ee.Feature(rfeat).intersection(sres_geom)
    )

    # ==========================================================================
    # [1] Process reaches that are both sources and sinks (small reservoirs)
    #     - remove upstream river outside reservoir
    #     - remove downstream river outside reservoir
    # ==========================================================================

    # Truncate source reaches (remove river outside of res)
    # Convert source reaches to line sections with boundary pts

    if debug_mode == True:
        reaches_sres_iolet_csas_list = reaches_sres_iolet_csas_ftc.toList(1000000)
        ilim = reaches_sres_iolet_csas_list.length().getInfo()

        sas_results_list = ee.List([])

        for i in range(0, ilim):
            input_rfeat = reaches_sres_iolet_csas_list.get(i)
            print("Source and sink input_rfeat")
            print(input_rfeat.getInfo(), "\n")
            t_output_rfeat = reach_to_lines_source_ftc(input_rfeat)
            output_rfeat = reach_to_lines_sink_ftc(t_output_rfeat)
            sas_results_list = sas_results_list.add(output_rfeat)

        inundated_river_csas_ftc = ee.FeatureCollection(sas_results_list)
    else:
        t_inundated_river_csas_ftc = reaches_sres_iolet_csas_ftc.map(
            reach_to_lines_source_ftc
        )
        inundated_river_csas_ftc = t_inundated_river_csas_ftc.map(
            reach_to_lines_sink_ftc
        )

    # ==========================================================================
    # [2] Process sinks; remove downstream river outside reservoir
    # ==========================================================================

    if debug_mode == True:
        reaches_sres_iolet_csink_list = reaches_sres_iolet_csink_ftc.toList(1000000)
        ilim = reaches_sres_iolet_csink_list.length().getInfo()

        sink_results_list = ee.List([])

        for i in range(0, ilim):
            input_rfeat = reaches_sres_iolet_csink_list.get(i)
            print("Sink input_rfeat")
            print(input_rfeat.getInfo(), "\n")
            output_rfeat = reach_to_lines_sink_ftc(input_rfeat)
            sink_results_list = sink_results_list.add(output_rfeat)

        inundated_river_csink_ftc = ee.FeatureCollection(sink_results_list)
    else:
        inundated_river_csink_ftc = reaches_sres_iolet_csink_ftc.map(
            reach_to_lines_sink_ftc
        )

    if debug_mode == True:
        print("[DEBUG] Sink")
        print(
            "[DEBUG] inundated_river_sink_ftc",
            inundated_river_csink_ftc.getInfo(),
            "\n",
        )

    # ==========================================================================
    # [2-a Optional] Export river sink reaches
    # ==========================================================================

    if cfg.exportSinkLines == True:
        msg = "Exporting sink lines"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(
                inundated_river_csink_ftc, c_dam_id_str, "river_sink_lines"
            )

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    # ==========================================================================
    # [3] Process sources; remove upstream river outside reservoir
    # ==========================================================================

    # Truncate source reaches (remove river outside of res)
    # Convert source reaches to line sections with boundary pts

    if debug_mode == True:
        reaches_sres_iolet_csource_list = reaches_sres_iolet_csource_ftc.toList(1000000)
        ilim = reaches_sres_iolet_csource_list.length().getInfo()

        source_results_list = ee.List([])

        for i in range(0, ilim):
            input_rfeat = reaches_sres_iolet_csource_list.get(i)
            print("Source input_rfeat")
            print(input_rfeat.getInfo(), "\n")
            output_rfeat = reach_to_lines_source_ftc(input_rfeat)
            source_results_list = source_results_list.add(output_rfeat)

        inundated_river_csource_ftc = ee.FeatureCollection(source_results_list)
    else:
        inundated_river_csource_ftc = reaches_sres_iolet_csource_ftc.map(
            reach_to_lines_source_ftc
        )

    if debug_mode == True:
        print("[DEBUG] Source")
        print(
            "[DEBUG] inundated_river_source_ftc",
            inundated_river_csource_ftc.getInfo(),
            "\n",
        )

    # ==========================================================================
    # [3-a Optional] Export river source lines
    # ==========================================================================

    if cfg.exportSourceLines == True:
        msg = "Exporting source lines"

        try:
            logger.info(f"{msg} {c_dam_id_str}")
            export.export_ftc(
                inundated_river_csource_ftc, c_dam_id_str, "river_source_lines"
            )

        except Exception as error:
            logger.exception(f"{msg} {c_dam_id_str}")

    # ==========================================================================
    # Prepare Final Output
    # ==========================================================================

    inundated_river_cftc = ee.FeatureCollection(
        ee.List(
            [
                inundated_river_ssas_ftc,
                inundated_river_csas_ftc,
                inundated_river_ssource_ftc,
                inundated_river_csource_ftc,
                inundated_river_ssink_ftc,
                inundated_river_csink_ftc,
                inundated_river_other_ftc,
            ]
        )
    )

    inundated_river_ftc = inundated_river_cftc.flatten()

    if debug_mode == True:
        print("[DEBUG]")
        print(
            "[DEBUG][delineate_river] Pre-flatten inundated_river_ftc",
            inundated_river_cftc.getInfo(),
            "\n",
        )
        print(
            "[DEBUG][delineate_river] inundated_river_ftc",
            inundated_river_ftc.getInfo(),
            "\n",
        )

    if cfg.exportRiver == True:
        inundated_river_main_ftc = find_main_channel(inundated_river_ftc, damFeat)
    else:
        inundated_river_main_ftc = inundated_river_ftc

    return (inundated_river_ftc, inundated_river_main_ftc)


def batch_delineate_rivers(c_dam_ids):

    for c_dam_id in c_dam_ids:

        # print ("[DEBUG] Processing", c_dam_id)
        c_dam_id_str = str(c_dam_id)

        reservoirAssetName = cfg.ps_geocaret_folder + "/" + "R_" + c_dam_id_str
        res_ftc = ee.FeatureCollection(reservoirAssetName)

        snappedAssetName = cfg.ps_geocaret_folder + "/" + "PS_" + c_dam_id_str
        damFeat = ee.FeatureCollection(snappedAssetName)

        riverVector, mainRiverVector = delineate_river(damFeat, res_ftc, c_dam_id_str)

        # ==========================================================================
        # Export river
        # ==========================================================================

        if cfg.exportRiver == True:
            # [5] Make catchment shape file (i) Find pixels
            msg = "Exporting river vector"

            try:
                logger.info(f" {msg} {c_dam_id_str}")
                export.export_ftc(riverVector, c_dam_id_str, "river_vector")

            except Exception as error:
                logger.exception(f"{msg} {c_dam_id_str}")
                mtr.active_analyses.remove(int(c_dam_id_str))
                continue

        # ==========================================================================
        # Export main river
        # ==========================================================================

        if cfg.exportMainRiver == True:
            # [5] Make catchment shape file (i) Find pixels
            # print ("[DEBUG] Exporting Main River", c_dam_id)
            msg = "Exporting main river vector"

            try:
                logger.info(f" {msg} {c_dam_id_str}")
                export.export_ftc(
                    mainRiverVector, c_dam_id_str, "main_river_vector"
                )

            except Exception as error:
                logger.exception(f"{msg} {c_dam_id_str}")
                continue


# ==============================================================================
# Development
# ==============================================================================


if __name__ == "__main__":

    print("Development Testing...")

    reservoirAssetName = "users/kkh451/XHEET/GAWLAN_20230126-1539/R_1201"
    res_ftc = ee.FeatureCollection(reservoirAssetName)

    snappedAssetName = "users/kkh451/XHEET/GAWLAN_20230126-1539/PS_1201"
    damFeat = ee.FeatureCollection(snappedAssetName)

    mainRiverVector, riverVector = delineate_river(damFeat, res_ftc, "1201")

    # Watch out for loss of parameters and polygon changes.
    # batch_delineate_rivers(["3077"])
