""" """

# TODO: Test and limit the number of try except blocks in the main body of this
# module.

from __future__ import annotations
from typing import Optional
import copy
import ee
import heet.gis.data as dta
import heet.monitor as mtr
import heet.log_setup
from heet.gis.dams import Dam, DamCollection
from heet.utils import get_package_file, read_config, set_logging_level
from heet.gis.data import HydroBasinsData
from heet.export import Exporter
from heet.gis.exceptions import NoOutletPointException
from heet.gis.helper import all_odd_or_zero, get_trail_A

# Create a logger and set logging level
logger = heet.log_setup.create_logger(logger_name=__name__)
logger_config: dict = read_config(
    get_package_file('./config/logging_levels.yaml'))
set_logging_level(logger=logger, level=logger_config['gis']['basins'])

# TODO: CURRENTLY ONLY EMISSIONS CONFIG FILES ARE CONSIDERED
#       MAKE THIS FILE CONFIGURABLE SO OTHER CONFGURATION FILES CAN BE PROVIDED
# Read config files and obtain config dictionaries
parameters: dict = read_config(file_name=get_package_file(
    './config/emissions/parameters.yaml'))
algo_config: dict = read_config(file_name=get_package_file(
    './config/emissions/parameters.yaml'))['algorithms']
export_config: dict = read_config(file_name=get_package_file(
    './config/emissions/exports.yaml'))[parameters['export_level']]
data_sources: dict = read_config(file_name=get_package_file(
    './config/emissions/data.yaml'))


class Basins:
    """ """
    # Base basins class - left blank and added as a placeholder in case
    # a deeper class hierarchy needs to be built


class HydroBasins(Basins):
    """Class for storing, manipulating and processing hydrobasins data."""

    def __init__(self, basins: HydroBasinsData):
        self._basins = basins
        self._exporter = None

    @classmethod
    def from_url(cls, data_url: str) -> HydroBasins:
        """ """
        source_data: dict = data_sources['hydrobasins']['url']
        return cls()

    @classmethod
    def from_config_data(cls, data_config: dict, level: int = 12):
        """ """

    def copy(self):
        """Create copy of the object."""
        return copy.deepcopy(self)

    def add_exporter(self, exporter: Exporter) -> None:
        self._exporter = exporter

    @property
    def exporter(self) -> Exporter:
        return self._exporter

    @exporter.setter
    def exporter(self, exporter: Exporter) -> None:
        self._exporter = exporter

    # Property setters making sure data consistency is enforced between
    # basins data and level
    @property
    def basins(self) -> HydroBasinsData:
        return self._basins

    @basins.setter
    def basins(self, level: int) -> None:
        self._basins = HydroBasinsData.fromsource(
            source=self._source_data[level], level=level)
        self._level = level

    @property
    def level(self) -> int:
        """ Get Hydrobasins level """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """Sets level (changes resolution) of the basins feature collection."""
        # Change the level only if the current level is diffent from the
        # specified level
        if self._level != level:
            self._level = level
            self._basins = HydroBasinsData.fromsource(
                source=self._source_data[level], level=level)

    @property
    def source_data(self) -> dict:
        return self._source_data


    def aggregate_by_hybasid(self) -> Optional[ee.List]:
        """Aggregate the basins over the 'HYBAS_ID' field and output a list of
        all hybas ids in the basins feature collection."""
        logger.info("Remove downstream sub-basins")
        try:
            upstream_subbasins_list = ee.List(
                self.basins.data.aggregate_array('HYBAS_ID'))
            return upstream_subbasins_list
        except ee.ee_exception.EEException as error:
            logger.exception("Remove downstream sub-basins")
            return None

    def outlet_subcatchment(self) -> ee.FeatureCollection:
        """Return outlet subcatchment defined by dam location."""
        if self.dam is not None:
            return self.basins.data.filterBounds(self.dam.geometry())
        raise NoOutletPointException()

    def get_subbasin(self, level: Optional[int] = None,
                     inplace: bool = True) -> ee.Dictionary:
        """ Get hydrobasins subbasin in which the dam is located in """
        # If inplace flag is True work on current object, otherwise create
        # a copy.
        if inplace is False:
            hydrobasins = self.copy()
        else:
            hydrobasins = self
        # If level is specified, make sure that the basins are at a required
        # level
        if level is not None:
            hydrobasins.level(level=level)
        logger.info(
            f"Finding the hydrobasins level {hydrobasins.level} sub-basin of the dam.")
        outlet_subcatch = hydrobasins.outlet_subcatchment()
        # Get the basins HYBAS_ID, PFAF_ID AND SPFAF_ID and return in
        # ee.Dictionary object
        hybas_id = ee.Number(
            ee.Feature(outlet_subcatch.first()).get('HYBAS_ID'))
        pfaf_id = ee.Number(
            ee.Feature(outlet_subcatch.first()).get('PFAF_ID'))
        spfaf_id = ee.Number(pfaf_id).format("%s")
        return ee.Dictionary({
            'PFAF_ID': pfaf_id,
            'SPFAF_ID': spfaf_id,
            'HYBAS_ID': hybas_id})

    def filter_by_id(
            self,
            id_field: str,
            id_value: ee.Number,
            level: Optional[int] = None,
            inplace: bool = False) -> Optional[HydroBasins]:
        """ """
        if inplace:
            hydrobasins = self
        else:
            hydrobasins = self.copy()

        if level is not None:
            # Check if the current level is equal to specified level.
            # If not, set the level before continuing
            hydrobasins.level = level

        hydrobasins.basins.data = hydrobasins.basins.data.filter(
            ee.Filter.eq(id_field, id_value))

        if not inplace:
            return hydrobasins

    def get_parents(self, children) -> ee.List:
        """ Given a hydrobasin subbasin and set of subbbasins to search within
            generate a list of direct parent sub-basins
        """
        parent_list = ee.List(children).map(
            lambda child:
            (self.basins.data
             .filter(ee.Filter.eq('NEXT_DOWN', child))
             .aggregate_array('HYBAS_ID')))
        distinct_parents = ee.List(parent_list).flatten().distinct()
        return distinct_parents

    def find_subbasins(self):
        """Caller of functions supporting all subbasin finding methods"""
        pass

    def find_subbasins_method_3(self) -> Optional[ee.List]:
        """ """
        def tag_upstream(feature: ee.Feature) -> ee.Feature:
            """ """
            A = outlet_pt_sbasin_12.get('SPFAF_ID')
            B = feature.get('SPFAF_ID')
            trail_A = get_trail_A(A, B)
            all_odd_zero = all_odd_or_zero(trail_A)
            feature = feature.set({'TRAIL_A': ee.String(trail_A)})
            feature = feature.set(
                {'ALL_ODD_OR_ZERO': ee.Number(all_odd_zero)})
            return feature

        try:
            logger.info(
                "Identifying upstream sub-basins from pfafstetter ids")
            self.basins.data = self.basins.data.map(tag_upstream)
            self.basins.data = self.basins.data.filter(
                ee.Filter.eq('ALL_ODD_OR_ZERO', ee.Number(1)))
        except ee.ee_exception.EEException:
            logger.exception(
                "Identifying upstream sub-basins from pfafstetter ids")
            return None
        return self.aggregate_by_hybasid()

    def find_hybas_bounding_level(self, inplace: bool = False) -> ee.Number:
        """Given a dam location, find the highest hydrobasins level which
        contains a subbasin that completely encloses the dam catchment.
        The method needs browse through a number of basin collections at
        different levels of detail. To avoid difficult to diagnose errors,
        the method works on a copy of the object, not on the curent object
        itself.
        """
        # If inplace=False, copy itself to ensure that we do not repetitively
        # change hydrobasin data (through setting the level setter property) in
        # the parent object.
        if inplace is False:
            hydrobasins = self.copy()
        else:
            hydrobasins = self

        logger.info("Finding the highest Hydrobasins level that encloses the catchment.")

        def algorithm(current, previous):
            previous = ee.List(previous)
            # Get previous level
            level = ee.Number.format(previous.length())
            # Set level to the previous level
            hydrobasins.level(level=level)
            # Get the outlet subcatchment for the current hybas level
            outlet_subcatch = hydrobasins.outlet_subcatchment()
            # Get the Hybas ID
            outlet_subcatch_id = ee.Number(
                ee.Feature(outlet_subcatch.first()).get('HYBAS_ID'))
            # Get parents for given outlet subcatchment  id
            ancestors = hydrobasins.get_parents(ee.List([outlet_subcatch_id]))
            ancestor_count = ee.Number(ee.List(ancestors).length())
            return_value = ee.Algorithms.If(
                ancestor_count.eq(0),
                ee.List([previous.length()]),
                ee.List([]))
            return previous.add(return_value)

        start = ee.List([[1]])
        indices_list = ee.List.sequence(0, 11, 1)
        ref_level = indices_list.iterate(algorithm, start)
        distinct_levels = ee.List(ref_level).flatten()
        # Return the bounding level as ee.Number
        return ee.Number(
            ee.List(distinct_levels).get(-1)).format("%s")

    #  Subbasin finding method 1 (trace ancestors)
    @staticmethod
    def get_ancestors(hybas_id: ee.Number,
                      subcatchments: HydroBasins) -> Optional[ee.List]:
        """
        Given a hydrobasins (12) subbasin hybas_id and set of hydrobasins (12)
        subbasins to search, trace upstream basins by following the NEXT_DOWN
        field. Should work with any hydrobasins dataset provided hybas_id and
        subbasin parameters are from the same level.

        While loops are not supported by EE, so we cannot specify a stopping
        condition (hybas_id not among NEXT_DOWNS). To keep all computation
        server-side we set the number of iterations to the number of
        sub-catchments to search less the number of source subbasins
        (no upstream) and empty results are filtered out.
        """
        def algorithm(current, previous):
            """ """
            child_list = ee.List(previous).get(-1)
            parent_list = ee.List(child_list).map(
                lambda child: (subcatchments.basins.data
                               .filter(ee.Filter.eq('NEXT_DOWN', child))
                               .aggregate_array('HYBAS_ID')))
            distinct_parents = ee.List(parent_list).flatten().distinct()
            return ee.List(previous).add(distinct_parents)

        try:
            logger.info("Finding upstream sub-basins by tracing ancestors")
            start_list = ee.List([]).add(ee.List([hybas_id]))
            logger.debug(
                f"[get_ancestors] Start list: {start_list.getInfo()}")
            logger.debug(
                f"[get_ancestors] Subcatchments size: {subcatchments.basins.data.size().getInfo()}")
            nodes = ee.List(
                subcatchments.basins.data.aggregate_array('HYBAS_ID')).distinct()
            next_nodes = ee.List(
                subcatchments.basins.data.aggregate_array('NEXT_DOWN')).distinct()
            sources = (
                ee.Number(ee.List(nodes).filter(
                    ee.Filter.inList('item', ee.List(next_nodes)).Not()).length()))
            max_iter = subcatchments.basins.data.size().add(1).subtract(sources)
            indices_list = ee.List.sequence(0, max_iter.subtract(1), 1)
            logger.debug(f"[get_ancestors] max_iter: {max_iter.getInfo()}")
            ancestors = indices_list.iterate(algorithm, start_list)
            distinct_ancestors = (
                ee.List(ancestors)
                .flatten()
                .distinct()
                .slice(1, None, 1))
        except ee.ee_exception.EEException as error:
            logger.exception(
                "Finding upstream sub-basins by tracing ancestors")
            distinct_ancestors = None

        return distinct_ancestors

    def remove_downstream_and_outside(
            self,
            pfaf_id: ee.Number,
            spfaf_id: ee.Number,
            level: int = 12,
            inplace: bool = True) -> Optional[HydroBasins]:
        """ """
        if inplace is True:
            hydrobasins = self
        else:
            hydrobasins = self.copy()
        hydrobasins.level = level
        logger.info("Removing downstream sub-basins and those outside the bounding basin from search.")
        # 1. Remove subbasins with a pfafsetter id greater than that of the
        # level 12 subbasin dam is in
        # 2. Restrict search to shared top-level basin
        try:
            hydrobasins.basins.data = \
                hydrobasins.basins.data\
                .filter(ee.Filter.gt('PFAF_ID', pfaf_id))\
                .filter(ee.Filter.stringStartsWith('SPFAF_ID', spfaf_id))\
                .sort('SORT', True)
        except ee.ee_exception.EEException:
            logger.exception(
                "Removing downstream sub-basins and those outside the bounding basin from search")
        if not inplace:
            return hydrobasins

    #  TODO: ADD Rivers object as an argument once River class is written.
    def batch_find_upstream_basins(
            self,
            dams: DamCollection,
            subbasin_find_method: int = algo_config['upstream_method']):
        """ """
        # Retrieve dams feature collection
        dams_ftc = dams.feature_collection
        # Define properties for exporting in raw_dam_pts
        selected_properties = ee.List(["country", "name", "id"])

        #  TODO: Change the iterator to iterate through dams.dams
        for c_dam_id in dams.c_dam_ids:
            c_dam_id_str = str(c_dam_id)
            # Get the dam feature matchig c_dam_id
            dam_feat = dams_ftc.filter(
                ee.Filter.eq('id', ee.Number(c_dam_id))).first()

            # 1. Export raw dam location
            if export_config['export_raw_dam_pts']:
                if self.exporter is None:
                    self.add_exporter(Exporter())
                name = "Raw dam location"
                logger.info(
                    f"Copying {name} id: {c_dam_id_str} to exporter object.")
                try:
                    ftc = ee.FeatureCollection(ee.Feature(dam_feat))
                    location_ftc = ftc.map(
                        lambda feat: ee.Feature(feat).select(selected_properties))
                    self.exporter.add_export(name=name,
                                             ft_collection=location_ftc,
                                             ft_id=c_dam_id_str)
                except ee.ee_exception.EEException as error:
                    logger.exception(
                        f"{error}. {name} could not be added to exporter.")
                    continue

            # 2. Snap Dam location to river Location
            try:
                dam = heet.gis.dams.Dam.from_feature(feature=dam_feat)
                dam.snap(rivers=ee.FeatureCollection(
                    data_sources['hydrorivers']['url']))
                snapped_dam_feat = dam.feature
                # Add snapped dam to the current HydroBasins object
                self.dam = dam
            except ee.ee_exception.EEException as error:
                logger.exception(f"{error}, Dam {c_dam_id_str} could not be snapped.")
                # TODO: Upgrade monitor functionality with mtr module
                mtr.active_analyses.remove(int(c_dam_id_str))
                continue

            # 3. Find upstream sub-basins
            try:
                # Find the highest hydrobasin level that completely encloses the
                # catchment
                outlet_pt_sbasin_bl = self.get_subbasin(
                    level=self.find_hybas_bounding_level())
                opt_bl_spfafid = outlet_pt_sbasin_bl.get('SPFAF_ID')
            except ee.ee_exception.EEException as error:
                logger.exception(
                    "Finding highest hydrobasin level and bounding " +
                    "basin that encloses the catchment.")
                continue

            try:
                # Find the hydrobasins level 12 subbasin ifo the dam is in
                outlet_pt_sbasin_12 = self.get_subbasin(level=12)

                dam_subbasin = self.filter_by_id(
                    id_field='HYBAS_ID',
                    id_value=outlet_pt_sbasin_12.get('HYBAS_ID'),
                    level=12, inplace=False)
                try:
                    dam_subbasin_feat = dam_subbasin.basins.data
                except AttributeError:
                    dam_subbasin_feat = None

            except ee.ee_exception.EEException as error:
                logger.info("Finding Highest Hydrobasins level that encloses the catchment")

            # Remove (filter out) subbasins that cannot be upstream of the dam
            # from hydrobasins 12 to limit search space
            filtered = self.remove_downstream_and_outside(
                pfaf_id=outlet_pt_sbasin_12.get('PFAF_ID'),
                spfaf_id=opt_bl_spfafid, level=12, inplace=False)

            # Find subbasins with different methods
            if subbasin_find_method == 1:
                upstream_subbasins_list = self.get_ancestors(
                    hybas_id=outlet_pt_sbasin_12.get('HYBAS_ID'),
                    subcatchments=filtered)
            if subbasin_find_method == 2:
                upstream_subbasins_list = filtered.aggregate_by_hybasid()
            if subbasin_find_method == 3:
                upstream_subbasins_list = filtered.find_subbasins_method_3()

            # TODO: Move this piece of code into the Dam class as a method
            # and reduce the dependency of the code on the ee.Feature
            snapped_dam_feat = snapped_dam_feat.set(
                'outlet_subcatch_id', outlet_pt_sbasin_12.get('HYBAS_ID'))
            snapped_dam_feat = snapped_dam_feat.set(
                'ancestor_ids',  ee.String.encodeJSON(upstream_subbasins_list))

            # TODO: Find a better way to export data in calculations
            if export_config['export_snapped_dam_pts']:
                if self.exporter is None:
                    self.add_exporter(Exporter())
                name = "Snapped dam location"
                logger.info(
                    f"Copying {name} id: {c_dam_id_str} to exporter object.")
                try:
                    ftc = ee.FeatureCollection(ee.Feature(snapped_dam_feat))
                    location_ftc = ftc.map(lambda feat: ee.Feature(feat))
                    self.exporter.add_export(name=name,
                                             ft_collection=location_ftc,
                                             ft_id=c_dam_id_str)
                except ee.ee_exception.EEException as error:
                    logger.exception(
                        f"{error}. {name} could not be added to exporter.")
                    continue


if __name__ == "__main__":
    hydrobasinsdata = HydroBasinsData.fromsource(
        source=data_sources['hydrobasins']['url'],
        level=12)
    basins = HydroBasins(level=12)
