import ee
import math
import logging

#==============================================================================
#  Set up logger
#==============================================================================

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


#==============================================================================
# Catchment, Reservoir, River Parameters
#==============================================================================
debug_mode = False

def terraclim_mghr(start_yr, end_yr, target_ftc):
   
    target_geom = target_ftc.geometry()
        
    target_var = ee.List(['srad'])
    target_var_scale_factor = ee.Number(0.1)
    target_years = ee.List.sequence(start_yr, end_yr)
    
    TERRACLIM =  ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select(target_var)
    # Expected SCALE = 4638

    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()   
        
    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_vars.getInfo())
    #print("[DEBUG]\n [terraclim_annual_mean]\n ", target_years.getInfo())
    
    # GHR is provided in W/m2 (J s-1 m-2) as a monthly time series
    # annual mean GHR in  kWh m-2 d-1 is required
    
    # Convert mean power per month to total energy per month
    # (multiply by seconds per month) and take the annual average

    # No consideration of leap years    

    days_per_month = ee.Dictionary({
        '1':  31, '2' : 28, '3' : 31,'4' : 30,'5' : 31,'6' : 30,
        '7' : 31, '8' : 31, '9' : 30,'10' :31,'11' : 30, '12' : 31
    })
    
    def mean_total_energy(k, v):

        month_no = ee.Number.parse(k)
        
        seconds_in_month = ee.Date.unitRatio('days', 'second').multiply(v)
        
        imgMonth = (
            TERRACLIM.filter(ee.Filter.calendarRange(start_yr, end_yr,'year'))
            .filter(ee.Filter.calendarRange(month_no, month_no,'month'))
            .map(lambda img : img.multiply(target_var_scale_factor).multiply(seconds_in_month))
        ).mean()
    
        return imgMonth

    # J m-2
    mean_total_energy_bymonth_dict = days_per_month.map(mean_total_energy)

    # All Months
    mghr_all = ee.Number(
        ee.ImageCollection(mean_total_energy_bymonth_dict.values())
         # Mean total annual energy; J m-2
        .sum()
        # Mean annual energy per day; J m-2 d-1
        .divide(ee.Date.unitRatio('year', 'days'))
        # Mean annual energy per day; kWh m-2 d-1
        .divide(3600000)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11
        }).get('srad'))
    
    
    mghr_nov_mar = ee.Number(
        ee.ImageCollection(mean_total_energy_bymonth_dict.select(**{'selectors': ['11', '12', '1', '2', '3']}).values())
         # Mean total annual energy; J m-2
        .sum()
        # Mean annual energy per day; J m-2 d-1
        #.divide(ee.Number(151))
        .divide(ee.Date.unitRatio('year', 'days').multiply(5/12))
        # Mean annual energy per day; kWh m-2 d-1
        .divide(3600000)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11            
        }).get('srad'))
    
    
    mghr_may_sept = ee.Number(
        ee.ImageCollection(mean_total_energy_bymonth_dict.select(**{'selectors': ['5', '6', '7', '8', '9']}).values())
         # Mean total annual energy; J m-2
        .sum()
        # Mean annual energy per day; J m-2 d-1
        #.divide(ee.Number(153))
        .divide(ee.Date.unitRatio('year', 'days').multiply(5/12))
        # Mean annual energy per day; kWh m-2 d-1
        .divide(3600000)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11            
        }).get('srad'))
    
    return(mghr_all, mghr_nov_mar, mghr_may_sept)
    

def terraclim_mghr_alt(start_yr, end_yr, target_ftc):
   
    target_geom = target_ftc.geometry()
        
    target_var = 'srad'
    target_var_scale_factor = ee.Number(0.1)
    target_years = ee.List.sequence(start_yr, end_yr)
    
    TERRACLIM =  ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select([target_var])
    # Expected SCALE = 4638

    projection = ee.Image(TERRACLIM.first()).projection()
    SCALE = projection.nominalScale()   

    # GHR is provided in W/m2 (J s-1 m-2) as a monthly time series
    # annual mean GHR in  kWh m-2 d-1 is required
    
    # Convert mean power per month to total energy per month
    # (multiply by seconds per month) and take the annual average

    # No consideration of leap years    
    
    def mean_annual_energy(year):

        is_leap = (
            ee.Number(year).mod(4).eq(0).And(
                (ee.Number(year).mod(100).neq(0)).Or
                (ee.Number(year).mod(400).eq(0))
        ))
        
        days_in_year = ee.Number(365).add(ee.Number(is_leap))
        
        def power_to_energy(k, v):
        
            month_no = ee.Number.parse(k)   
            days_in_month = ee.Number(v).add(ee.Number(is_leap).multiply(month_no.eq(2)))
            seconds_in_month = ee.Date.unitRatio('days', 'second').multiply(days_in_month)
                  
            month_img = (TERRACLIM
              .filter(ee.Filter.calendarRange(year, year,'year'))
              .filter(ee.Filter.calendarRange(month_no, month_no,'month'))
              .map(lambda img : img.multiply(target_var_scale_factor).multiply(seconds_in_month))            
            )

            return(month_img)
      
        annual_img = target_months.map(power_to_energy).sum().divide(days_in_year).divide(3600000)
        return annual_img

    # All Months
    target_months = ee.Dictionary({
        '1':  31, '2' : 28, '3' : 31,'4' : 30,'5' : 31,'6' : 30,
        '7' : 31, '8' : 31, '9' : 30,'10' :31,'11' : 30, '12' : 31
    })
    
    mean_total_energy_byyear = target_years.map(mean_annual_energy)

    mghr_all = ee.Number(
        ee.ImageCollection(mean_total_energy_byyear)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11 
        }).get('srad'))
    
    # May september
    target_months = ee.Dictionary({
        '5' : 31,'6' : 30, '7' : 31, '8' : 31, '9' : 30
    })

    mean_total_energy_ms_byyear = target_years.map(mean_annual_energy)

    mghr_may_sept = ee.Number(
        ee.ImageCollection(mean_total_energy_ms_byyear)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11             
        }).get('srad'))
    
    
    def mean_energy_nm(year):
        
        def is_leap_yr(year):
            is_leap = (
                ee.Number(year).mod(4).eq(0).And(
                    (ee.Number(year).mod(100).neq(0)).Or
                    (ee.Number(year).mod(400).eq(0))
            ))
            return is_leap
                
        def power_to_energy(k, v):
            
            is_leap =  is_leap_yr(year)
            
            month_no = ee.Number.parse(k)   
            days_in_month = ee.Number(v).add(ee.Number(is_leap).multiply(month_no.eq(2)))
            seconds_in_month = ee.Date.unitRatio('days', 'second').multiply(days_in_month)
                  
            month_img = (TERRACLIM
              .filter(ee.Filter.calendarRange(year, year,'year'))
              .filter(ee.Filter.calendarRange(month_no, month_no,'month'))
              .map(lambda img : img.multiply(target_var_scale_factor).multiply(seconds_in_month))            
            )

            return(month_img)
      
        
        days_in_year1 = ee.Number(61)        
        annual_img1 = target_months_a.map(power_to_energy).sum()
        
        is_leap = is_leap_yr(year)
        days_in_year2= ee.Number(90).add(is_leap)
        annual_img2 = target_months_b.map(power_to_energy).sum()
        
        days_in_year  = days_in_year1.add(days_in_year2) 
        annual_img = annual_img1.addBands(annual_img2).sum().divide(days_in_year).divide(3600000)
        
        return annual_img
    
     # All Months
    target_months_a = ee.Dictionary({
        '11' : 30, '12' : 31
    })  
    
    target_months_b = ee.Dictionary({
        '1':  31, '2' : 28, '3' : 31
    })   
    
    mean_total_energy_nm_byyear = target_years.map(mean_energy_nm)

    mghr_nov_mar = ee.Number(
        ee.ImageCollection(mean_total_energy_nm_byyear)
        .reduceRegion(**{
            'reducer': ee.Reducer.mean(),
            'geometry': target_geom,
            'scale': SCALE,
            'maxPixels':2e11             
        }).get('srad'))
    
    
    return(mghr_all, mghr_may_sept, mghr_nov_mar)


#==============================================================================
# Reservoir Parameters
#==============================================================================

def mean_annual_runoff_mm_gldas(catchment_ftc): 
    
    GLDAS = ee.ImageCollection("NASA/GLDAS/V021/NOAH/G025/T3H");

    # Expected SCALE = 27830
    projection = ee.Image(GLDAS.first()).projection()
    SCALE = projection.nominalScale()       
    
    catch_geom = catchment_ftc.geometry()
    
    #==================================================================
    # PRESW
    #==================================================================
    # 
    # Runoff: [kg/m2]
    #  - Qs_acc  : Storm surface runoff
    #  - Qsb_acc : Baseflow-groundwater runoff
    #  - Qsm_acc : Snow melt
    #
    #==================================================================
    
    factor_3hrs_to_s = ee.Number(3).multiply(60).multiply(60)
    target_vars = ['ro_kg']

    def prepare_gldas_img(img):
        
        # Qs_acc  : Storm surface runoff
        # Qsb_acc : Baseflow-groundwater runoff
        # Qsm_acc : Snow melt
        
        rimg = (img.select(['Qs_acc','Qsb_acc','Qsm_acc'])
            .reduce('sum')
            .multiply(ee.Image.pixelArea())
            .rename(['ro_kg']))
    
        aimg = ee.Image.pixelArea()      
        
        uimg = (ee.Image(img)
            .addBands(rimg)
            .addBands(aimg))
      
        return(uimg)        

    PGLDAS = GLDAS.map(prepare_gldas_img)
    
        
    baseStartDate = ee.Date('2000-01-01')
    years = ee.List.sequence(0, 20)

    def gen_target_years(adv):
        startDate = baseStartDate.advance(adv,'years')
        endDate = baseStartDate.advance(ee.Number(adv).add(1),'years')

        i = ee.Number(adv).add(1)
        
        return(ee.List([startDate, endDate, i]))

    
    target_years = years.map(gen_target_years)
      
    
    # Group by year, and then reduce within groups by sum();
    # the result is an ImageCollection with one image for each
    # year.

    def gen_yearly_img(r) :
                
        s = ee.List(r).get(0)
        e = ee.List(r).get(1)
        y = ee.List(r).get(2)
        
        return (PGLDAS.filter(ee.Filter.date(s, e))
                    .select(target_vars).sum().set('year', y))
         
    
    AGLDAS = ee.ImageCollection.fromImages(
          target_years.map(gen_yearly_img)
    )
        
    catch_area_m = catch_geom.area()
    
    def get_regional_value(img, first) :
      
        stats = img.reduceRegion(**{
            'reducer': ee.Reducer.sum(),
            'geometry': catch_geom,
            'scale': SCALE,
            'maxPixels':2e11            
        })
      
      
        metrics = stats.toArray(target_vars).toList()
        returnValue = ee.List(first).add(metrics)
      
        return returnValue
    
    
    results = ee.List([])
    metrics = AGLDAS.iterate(get_regional_value,results)
    
    t_regional_metrics_yearly = ee.List(metrics).unzip()

    if debug_mode == True:       
        print("[DEBUG] [mean_annual_runoff_mm_gldas]", t_regional_metrics_yearly.getInfo)
    
    mean_annual_values = t_regional_metrics_yearly.map( lambda ts :
        ee.Number(ee.List(ts).reduce('mean')).divide(catch_geom.area())
    )
    
    if debug_mode == True:       
        print("[DEBUG]")
        #print("[DEBUG] [mean_annual_runoff_mm_gldas] Target Years", target_years.getInfo())
        #print("[DEBUG] [mean_annual_runoff_mm_gldas] AGLDAS", AGLDAS.getInfo())
        #print("[DEBUG] [mean_annual_runoff_mm_gldas] Mean Values", mean_annual_values.getInfo())
    
    return mean_annual_values



#==============================================================================
# Draft Parameters
#==============================================================================
"""

Terraclimate MGHR

    # terraclim_mghr(2000, 2019, catchment_ftc)    
    # terraclim_mghr_alt(2000, 2019, catchment_ftc)    
    
    maghr_kwhperm2perday_alt1 = "UD"
    mghr_all_kwhperm2perday_alt1 = "UD"
    mghr_nov_mar_kwhperm2perday_alt1 = "UD"
    mghr_may_sept_kwhperm2perday_alt1 = "UD"

GLDAS 
    mar_mm_alt1 =  "UD"
    
"""





    
  