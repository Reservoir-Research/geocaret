""" Functions for cleaning up Earth Engine assets """
import argparse
import ee

ee.Initialize()


def find_child_assets(search_list: list) -> list:
    """Find assets on Earth Engine"""
    search_list = [a for a in search_list if a["type"] in ["FOLDER", "IMAGECOLLECTION"]]

    new_asset_collection = []
    search_next = []

    for target_asset in search_list:
        found = ee.data.listAssets({"parent": target_asset["name"]})
        if "assets" in found:
            new_asset_collection.extend(found["assets"])
            search_next.extend(found["assets"])
    return search_next, new_asset_collection


def find_assets(search_list: list, asset_collection: list) -> list:
    """Find assets on Earth Engine"""
    search_next, new_asset_collection = find_child_assets(search_list)
    asset_collection.extend(new_asset_collection)

    while len(search_next) > 0:
        search_next, new_asset_collection = find_child_assets(search_next)
        asset_collection.extend(new_asset_collection)

    return asset_collection


def delete_folder(target_folder: str) -> None:
    """Delete assets in target folder in Earth Engine"""
    geocaret_assets = ee.data.listAssets({"parent": target_folder})
    asset_collection = geocaret_assets["assets"]
    if len(asset_collection) > 0:
        assets_to_delete = find_assets(geocaret_assets["assets"], asset_collection)
        # print(assets_to_delete)
        assets_to_delete.reverse()
        for target_asset in assets_to_delete:
            ee.data.deleteAsset(target_asset["name"])
    ee.data.deleteAsset(target_folder)


parser = argparse.ArgumentParser(
    description="Delete a google earth engine asset folder, "
    + "all subfolders and content."
)
parser.add_argument(
    "target", type=str, help="Path to earth engine asset folder to delete."
)


def main():
    """Clean target folder on Earth Engine"""
    args = parser.parse_args()
    # print(args)
    target = args.target
    root_folder = ee.data.getAssetRoots()[0]["id"]
    target_folder = root_folder + "/" + target
    delete_folder(target_folder)


if __name__ == "__main__":
    main()
