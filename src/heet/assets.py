""" """
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import pathlib
import yaml
import ee
from heet.utils import get_package_file
from heet.web.earth_engine import EarthEngine
from heet.exceptions import NoRootFolderException
from heet.web.connectivity import internet_error_handler
import heet.log_setup

# Create a logger
logger = heet.log_setup.create_logger(logger_name=__name__)


class Asset(ABC):
    """ Wrapper for Google's Earth Engine asset objects """
    folder_prefix = "A_"

    def __init__(self, id: str, asset_folder: str, name: Optional[str] = None):
        self.id = id
        self.asset_folder = asset_folder
        if name is not None:
            self.name = name
        else:
            self.name = asset_folder + "/" + self.folder_prefix + id

    @abstractmethod
    def data(self):
        """ """


class ReservoirAsset(Asset):
    """Class storing Reservoir asset data"""
    folder_prefix = "R_"

    def data(self):
        pass


class SnappedAsset(Asset):
    """Class storing snapped dam asset data"""
    folder_prefix = "PS_"

    def data(self):
        pass


class Assets:
    """ Class containing the assets, GIS layers, and processed data and methods
        for uploading to and downloding from Google's Earth Engine """

    # Only the below asset types are considered assets
    asset_types = ["FOLDER", "IMAGECOLLECTION"]

    def __init__(self, working_folder: str, config_file: pathlib.PosixPath):
        _ = EarthEngine().init()
        with open(config_file, "r", encoding="utf8") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)['assets']
        self.working_folder = working_folder

        self.output_drive_folder = ""
        self.output_asset_folder_name = ""

    @property
    def assets(self) -> Dict[str, List[Dict[str, str]]]:
        """Find all assets in the working project folder.

        Returns:
            A dictionary with key 'assets' and values being a list of
                dictionaries with keys: `type`, `name` and `id`.
        """
        return ee.data.listAssets({'parent': self.working_folder})

    @property
    def buckets(self) -> Dict[str, List[Dict[str, str]]]:
        """Find all buckets, i.e. assets that are of type 'FOLDER'.

        Returns:
            A dictionary with key 'assets' and values being a list of
                dictionaries with keys: `type`, `name` and `id` where
                `type` == 'FOLDER'.
        """
        return ee.data.listBuckets()

    @property
    def asset_folders(self) -> List[Dict[str, str]]:
        """
        Return the list of the root folders the user owns where asset types
        are in `type` and asset identifiers in `id`.
        """
        return ee.data.getAssetRoots()

    @property
    def root_folder(self) -> str:
        """
        Return id (name) of the first root folder if present.

        Raises:
            NoRootFolderException.
        """
        if self.asset_folders:
            root_folder = self.asset_folders[0]['id']
            return root_folder
        raise NoRootFolderException()

    @property
    def username(self) -> str:
        """
        Return user name if root folder present, otherwise raise
        NoRootFolderException.
        """
        if self.asset_folders:
            return ee.data.getAssetRoots()[0]['id'].split("/")[-1]
        raise NoRootFolderException(
            message=("Root folder in your Google Earth's account is required " +
                     "to retrieve your user name.\nCreate a home folder and " +
                     "try again."))

    @staticmethod
    @internet_error_handler
    def create_root(root_folder: str) -> None:
        """ Creates a home root folder in users's Google Earth's account

        Args:
            root_folder (str):
        """
        try:
            ee.data.createAssetHome(root_folder)
        except ee.ee_exception.EEException:
            logger.info('Home root folder %s already exists.', root_folder)

    def existing_job_files(self) -> bool:
        """Return True if job files are present in the application folder in
        the Google's Earth Engine user's account. Otherwise, return False."""
        # TODO: Decide how to deal with interrupted internet connctions.
        heet_assets = ee.data.listAssets({'parent': self.working_folder})
        return bool(len(heet_assets['assets']) > 0)

    def clear_folder(self, target_folder: str) -> None:
        """ Delete assets in target folder in Earth Engine """
        assets = ee.data.listAssets({'parent': target_folder})
        asset_collection = assets['assets']
        if len(asset_collection) > 0:
            assets_to_delete = self.find_assets(
                assets['assets'], asset_collection)
            # print(assets_to_delete)
            assets_to_delete.reverse()
            for target_asset in assets_to_delete:
                ee.data.deleteAsset(target_asset['name'])
                logger.info(f"Deleting {target_asset['name']}")
        ee.data.deleteAsset(target_folder)

    def clear_working_folder(self) -> None:
        self.clear_folder(target_folder=self.working_folder)

    def create_assets_folder(self) -> None:
        """ fix non-specific exception handling...... """
        try:
            self.clear_working_folder()

        except Exception as error:
            # Assume first run (no Heet folder)
            subfolders = self.config['heet_folder'].split("/")
            target_path = self.root_folder

            for subfolder in subfolders:
                target_path = target_path + "/" + subfolder
                try:
                    ee.data.getAsset(target_path)
                except:
                    ee.data.createAsset({'type': 'Folder'}, target_path)

    def find_child_assets(self, search_list: list):
        """
        Find assets on Earth Engine
        TODO: Understand what the method is doing and provide description. """
        asset_search_list = [
            a for a in search_list if a['type'] in
            self.asset_types]
        new_asset_collection = []
        search_next = []
        for target_asset in asset_search_list:
            found = ee.data.listAssets({'parent': target_asset['name']})
            if 'assets' in found:
                new_asset_collection.extend(found['assets'])
                search_next.extend(found['assets'])
        return search_next, new_asset_collection

    def find_assets(self, search_list: list, asset_collection: list) -> list:
        """ Find assets on Earth Engine
        TODO: Understand what the method is doing and provide description. """
        search_next, new_asset_collection = self.find_child_assets(search_list)
        asset_collection.extend(new_asset_collection)
        while len(search_next) > 0:
            search_next, new_asset_collection = \
                self.find_child_assets(search_next)
            asset_collection.extend(new_asset_collection)
        return asset_collection


    def download(self) -> None:
        """ """
        pass


class EmissionAssets(Assets):
    """Class derived from the generic EarthEngine's Asset class designed
    specifically to work with assets used for processing GIS data required to
    derived inputs requied for calculating greenhouse gas emissions from
    reservoirs.
    """
    def __init__(
            self,
            config_file: pathlib.PosixPath = get_package_file(
                './config/emissions/parameters.yaml'),
            working_folder=""):
        super().__init__(
            working_folder=working_folder,
            config_file=config_file)
        self.working_folder = self.root_folder + "/" + \
            self.config['heet_folder']
        self.dams_table_path = self.working_folder + "/" + "user_inputs"


if __name__ == '__main__':
    a = EmissionAssets()
    print('Assets:')
    print(a.assets['assets'])
    print('Child assets:')
    #print(a.find_child_assets(a.assets['assets']))
    print(a.find_child_assets(a.assets['assets']))
