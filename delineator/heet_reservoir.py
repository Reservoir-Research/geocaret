import ee
import heet_config as cfg
import heet_data as dta
import heet_export
import logging

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('heet.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

debug_mode = False

def simplify_reservoir(r_ftc, c_dam_id_str):
        r_geometry = r_ftc.geometry()
      
        def extract_polygons(feat):
            
            polyFeat= ee.Geometry.Polygon(ee.Geometry(feat).coordinates())
            polyFeat = ee.Feature(polyFeat).set('area_m', polyFeat.area(**{'maxError': 1}))

            return(polyFeat)
        
        # Simplify reservoir geometry (outer boundary)
        r_all_geometries = r_geometry.geometries()
        r_polygons = ee.FeatureCollection(r_all_geometries.map(extract_polygons));
    
        properties = ['area_m']
        largest_area = (r_polygons
            .reduceColumns(**{
              'reducer': ee.Reducer.max(),
              'selectors': properties
            }).get('max')
        )
  
        outer_boundary = r_polygons.filter(ee.Filter.eq('area_m', largest_area))
        
        # First OK; used to select largest feature
        sr_geometry = outer_boundary.first().geometry()
  
        sr_vector = ee.FeatureCollection(ee.Feature(sr_geometry))
        #==========================================================================
        # Export simplified reservoir
        #==========================================================================
       
        if cfg.exportSimplifiedReservoir == True: 
            msg = "Exporting simplified reservoir"     
            
            try:
                logger.info(f'{msg} {c_dam_id_str}')
                heet_export.export_ftc(sr_vector, c_dam_id_str, "simple_reservoir_vector")
                                        
            except Exception as error:
                logger.exception(f'{msg} {c_dam_id_str}')
        
        return ee.FeatureCollection(ee.Feature(sr_geometry))
    

def batch_delineate_reservoirs(c_dam_ids) :
    
    for c_dam_id in c_dam_ids:  
        
        c_dam_id_str = str(c_dam_id)
    
        snapped_point_name = cfg.ps_heet_folder + "/" + "PS_" + c_dam_id_str
        
        # First OK; single feature
        damFeat = ee.FeatureCollection(snapped_point_name).first()
    
        catchmentAssetName =  cfg.ps_heet_folder + "/" + "C_" + c_dam_id_str
        catchmentVector = ee.FeatureCollection(catchmentAssetName)
        
        reservoirVector= delineate_reservoir(damFeat, catchmentVector, c_dam_id_str)
                   
        #==========================================================================
        # Export reservoir
        #==========================================================================
       
        # [5] Make catchment shape file (i) Find pixels
        msg = "Exporting reservoir vector"     
        
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            if cfg.exportReservoirVector == True:
                reservoirVectorFeat = ee.Feature(reservoirVector)
                reservoirVectorFeat = reservoirVectorFeat.copyProperties(**{'source': damFeat, 'exclude' : ['ancestor_ids']})
                
                heet_export.export_ftc(ee.FeatureCollection(ee.Feature(reservoirVectorFeat)), c_dam_id_str, "reservoir_vector")
                                        
        except Exception as error:
            logger.exception(f'{msg} {c_dam_id_str}')
            mtr.active_analyses.remove(int(c_dam_id_str))              
            continue    

            

def delineate_reservoir(damFeat, catchmentVector, c_dam_id_str):
  
    if debug_mode == True:
        cfg.exportWaterbodies = True
        
    #============================================================================
    # Load Source Data
    #============================================================================
    SRTM = ee.Image("USGS/SRTMGL1_003")
    
    #============================================================================
    #  Set user-specified parameters
    #============================================================================
    
    damFeat = ee.Feature(damFeat)
    dam_point = damFeat.geometry()
    
    dam_longitude = ee.Number(dam_point.coordinates().get(0))
    dam_latitude = ee.Number(dam_point.coordinates().get(1))
    
    # First OK; r_imputed_water_level is a collection level property, duplicated
    # over all features.
    water_level_str = ee.FeatureCollection(catchmentVector).first().get('r_imputed_water_level')
    water_level = ee.Number.parse(water_level_str)
    
    catchment_geometry = catchmentVector.geometry()
    
    DEM = SRTM
    projection = ee.Image(DEM).projection()
    
    # expected SCALE = 30
    SCALE = projection.nominalScale() 
  
    #==============================================================================
    # Pre-process Inputs
    #==============================================================================
    
    # Dam location
    dam_point_location = ee.Geometry.Point(dam_longitude, dam_latitude)
    
    #==============================================================================
    # Determine reservoir
    #==============================================================================
    
    # Minimum elevation at dam site
    dam_elevation_min = DEM.reduceRegion(**{
      'reducer' : ee.Reducer.min(),
      'geometry': dam_point_location,
      'scale': SCALE,
      'maxPixels': 2e11
    }).get('elevation')
    
    #print("Dam elevation:",dam_elevation_min) 
    
    # Set water level
    #  Dam height is a proxy for full supply level.
    water_elevation = ee.Number(dam_elevation_min).add(water_level)
   
    # print("Water elevation:",water_elevation) 
    
    # Pixels of lower elevation than water level are inundated
    inundated_area = DEM.clip(catchment_geometry).lte(ee.Number(water_elevation))
    inundated_area = inundated_area.selfMask()

    #==========================================================================
    # Export inundated pixels
    #==========================================================================
   
    if cfg.exportReservoirPixels == True: 
        msg = "Exporting inundated pixels"     
        
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            heet_export.export_image(inundated_area, c_dam_id_str, "waterbodies_pixels")
                                    
        except Exception as error:
            logger.exception(f'{msg} {c_dam_id_str}')
              

    #logger.debug("\n [delineate_reservoir] water_elevation", water_elevation.getInfo()) 
      
    water_bodies = inundated_area.reduceToVectors(**{
      'reducer': ee.Reducer.countEvery(),
      'geometry': catchment_geometry, 
      'scale': SCALE,
      'maxPixels': 2e11
    })
    
    
    #==========================================================================
    # Export waterbodies
    #==========================================================================
   
    if cfg.exportWaterbodies == True: 
        msg = "Exporting waterbodies vector"     
        
        try:
            logger.info(f'{msg} {c_dam_id_str}')
            heet_export.export_ftc(water_bodies, c_dam_id_str, "waterbodies_vector")
                                    
        except Exception as error:
            logger.exception(f'{msg} {c_dam_id_str}')
              
            
    if debug_mode == True:
        print("\n [delineate_reservoir] water_bodies", water_bodies.getInfo()) 
        print("\n [delineate_reservoir] dam_point_location", dam_point_location.getInfo())     
      

    # logger.debug("\n [delineate_reservoir] main_water_body", main_water_body.getInfo()) 
    #==============================================================================
    # Select water body that intersects the dam point
    #==============================================================================
    
    # Filters out the water bodies that don't intersect the dam
    reservoirVector = ee.FeatureCollection(
            water_bodies.filterBounds(dam_point_location)
    ).first()

    if debug_mode == True:
        print("\n [delineate_reservoir] reservoirVector", reservoirVector.getInfo()) 
        print("\n [delineate_reservoir] water_level_str", water_level_str.getInfo())  
    
    reservoirVector = ee.Feature(reservoirVector).set("_imputed_water_level", water_level_str)
    #logger.debug("\n [delineate_reservoir] reservoirVector", reservoirVector.getInfo()) 
      
    return(reservoirVector)       

#==============================================================================
# Development 
#==============================================================================


if __name__ == "__main__":
    
    print("Development run ...")

    catchmentAssetName = "users/KamillaHarding/XHEET/AFRICA2_20220222-1303/C_3080"
    catchment_ftc = ee.FeatureCollection(catchmentAssetName)
    damAssetName = "users/KamillaHarding/XHEET/AFRICA2_20220222-1303/PS_3080"
    dam_ftc = ee.FeatureCollection(damAssetName).first()
    
    reservoirVector = delineate_reservoir(dam_ftc, catchment_ftc, "3080")
    #batch_delineate_reservoirs('[3080]')
    

