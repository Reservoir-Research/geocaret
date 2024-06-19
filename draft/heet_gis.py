import ee


def ee_image_mean_geom(gis_layer, target_geom, target_var, scale_factor = 1):
    
    GIS_LAYER = (
        ee.Image(gis_layer)
    )

    projection = ee.Image(GIS_LAYER).projection()
    SCALE = projection.nominalScale()

    stats = GIS_LAYER.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': target_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    })

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(
            ee.Algorithms.IsEqual(v, None), 
            -999, 
            ee.Number(stats.get(k)).multiply(scale_factor)
        )
    )
    metric = stats.get(target_var) 

    return(metric)

def ee_image_min_geom(gis_layer, target_geom, target_var, scale_factor = 1):
    
    GIS_LAYER = (
        ee.Image(gis_layer)
    )

    projection = ee.Image(GIS_LAYER).projection()
    SCALE = projection.nominalScale()

    stats = GIS_LAYER.reduceRegion(**{
        'reducer': ee.Reducer.min(),
        'geometry': target_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    })

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(
            ee.Algorithms.IsEqual(v, None), 
            -999, 
            ee.Number(stats.get(k)).multiply(scale_factor)
        )
    )
    metric = stats.get(target_var) 

    return(metric)

def ee_image_max_geom(gis_layer, target_geom, target_var, scale_factor = 1):
    
    GIS_LAYER = (
        ee.Image(gis_layer)
    )

    projection = ee.Image(GIS_LAYER).projection()
    SCALE = projection.nominalScale()

    stats = GIS_LAYER.reduceRegion(**{
        'reducer': ee.Reducer.max(),
        'geometry': target_geom,
        'scale': SCALE,
        'maxPixels': 2e11
    })

    stats = stats.map(
        lambda k, v: ee.Algorithms.If(
            ee.Algorithms.IsEqual(v, None), 
            -999, 
            ee.Number(stats.get(k)).multiply(scale_factor)
        )
    )
    metric = stats.get(target_var) 

    return(metric)

def ee_ftc_mean_geom(gis_layer, target_geom, target_var, scale_factor = 1):

    GIS_LAYER = ee.FeatureCollection(gis_layer)

    column_mean = (GIS_LAYER
            .filterBounds(target_geom)
            .reduceColumns(ee.Reducer.mean(), [target_var])
            .get('mean')
    )
    return(column_mean)


def ee_ftc_mode_geom(gis_layer, target_ftc, target_var):

    GIS_LAYER = ee.FeatureCollection(gis_layer)

    target_geom = target_ftc.geometry()
    target_geom_buffer = target_geom.buffer(500)
    target_geom_bbox = target_geom_buffer.bounds()
    target_geom_area_m = target_geom.area(1)

    def get_overlap(feat):

        # Define feature geometry
        geom = ee.Feature(feat).geometry()

        # Calculate the area of the feature geometry
        areaGisZone = geom.area(1)

        # Calculate that area of the target geometry
        # that intersects with each category (A_Inter)
        unionCategories = aTARGET.filterBounds(geom).union().first().geometry()
        A_Inter = unionCategories.intersection(geom, 1).area(1)

        # Divide A_Inter/target_geom_area_m to calculate the 
        # percentage of target geometry area within the gis category
        perc = A_Inter.divide(target_geom_area_m).multiply(100)

        return ee.Feature(feat).setMulti({'AreaGIS': areaGisZone, 'AreaTarget': target_geom_area_m, 'PercentageGIS': perc})

    # Put a bounding box around the target geometry
    # to speed up computation
    aTARGET = target_ftc.filterBounds(target_geom_bbox)
    aGIS = GIS_LAYER.filterBounds(target_geom_bbox)

    # Calculate area of overlap between the target geometry and gis category
    targetGIS = aGIS.map(get_overlap)

    gis_percentages = targetGIS.aggregate_array('PercentageGIS')
    gis_names = targetGIS.aggregate_array(target_var)
    index_pb = ee.Array(gis_percentages).argmax().get(0)
    modal_value = gis_names.get(index_pb)

    return modal_value

def ee_ic_layer_monthly_mean(gis_layer, start_yr, end_yr, target_vars):

    GIS_LAYER = ee.ImageCollection(gis_layer).select(target_vars)

    date_start = ee.Date.fromYMD(start_yr, 1, 1)
    date_end = ee.Date.fromYMD(end_yr, 1, 1).advance(1, "year")

    monthly_mean_img = (GIS_LAYER 
                .filterDate(date_start, date_end)
                .mean()
                .set({'system:time_start': date_start}))

    return(monthly_mean_img)


def ee_ic_layer_annual_mean(gis_layer, start_yr, end_yr, target_vars):

    GIS_LAYER = ee.ImageCollection(gis_layer).select(target_vars)
    target_years = ee.List.sequence(start_yr, end_yr)

    def annual_sum(year):

        date_start = ee.Date.fromYMD(year, 1, 1)
        date_end = date_start.advance(1, "year")

        year_img = (GIS_LAYER
                    .filterDate(date_start, date_end)
                    .sum()
                    .set({'year': year, 'system:time_start': date_start}))
        return(year_img)

    # Convert monthly image collection to yearly sums
    metric_yearly_cimg = ee.ImageCollection(target_years.map(annual_sum))

    # Mean of yearly totals
    annual_mean_img = metric_yearly_cimg.mean()

    return annual_mean_img