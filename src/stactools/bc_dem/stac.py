import logging
import os
from typing import Optional

import fsspec
import rasterio
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    SpatialExtent,
    TemporalExtent,
)
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import (
    DataType,
    RasterBand,
    RasterExtension,
    Sampling,
)
from shapely.geometry import box, mapping
from stactools.core.io import ReadHrefModifier

from stactools.bc_dem.constants import (
    COLLECTION_ID,
    CRS_WKT,
    DESCRIPTION,
    EPSG,
    LICENSE,
    LICENSE_LINK,
    NO_DATA,
    PROVIDERS,
    SPATIAL_EXTENT,
    SPATIAL_RESOLUTION,
    START_DATE,
    TEMPORAL_EXTENT,
    THUMBNAIL_HREF,
    TITLE,
    UNIT,
)

logger = logging.getLogger(__name__)


def create_collection() -> Collection:

    collection = Collection(
        id=COLLECTION_ID,
        title=TITLE,
        description=DESCRIPTION,
        license=LICENSE,
        providers=PROVIDERS,
        extent=Extent(
            SpatialExtent([SPATIAL_EXTENT]),
            TemporalExtent(TEMPORAL_EXTENT),
        ),
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )
    collection.add_link(LICENSE_LINK)

    collection.add_asset(
        "thumbnail",
        Asset(
            href=THUMBNAIL_HREF,
            media_type=MediaType.JPEG,
            roles=["thumbnail"],
            title="DEM Thumbnail",
        ),
    )

    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [EPSG]

    collection_item_assets = ItemAssetsExtension.ext(collection,
                                                     add_if_missing=True)

    collection_item_assets.item_assets = {
        "DEM_Lidar":
        AssetDefinition({
            "type":
            MediaType.COG,
            "roles": [
                "data",
                "DEM",
                "raster",
            ],
            "title":
            "DEM from BC Lidar",
            "raster:bands": [
                RasterBand.create(sampling=Sampling.AREA,
                                  data_type=DataType.UINT8).to_dict()
            ],
            "proj:epsg":
            collection_proj.epsg,
        }),
    }
    return collection


def create_item(
    cog_href: str,
    cog_read_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:

    if cog_read_href_modifier:
        cog_access_href = cog_read_href_modifier(cog_href)
    else:
        cog_access_href = cog_href

    with rasterio.open(cog_access_href) as dataset:
        bbox = list(dataset.bounds)
        geometry = mapping(box(*bbox))
        transform = dataset.transform
        shape = dataset.shape

    # TODO: Get the year of the tile. From the filename?
    item = Item(
        id=os.path.splitext(os.path.basename(cog_href))[0],
        geometry=geometry,
        bbox=bbox,
        datetime=START_DATE,
        properties={},
        stac_extensions=[],
    )

    item.common_metadata.resolution = SPATIAL_RESOLUTION
    item.common_metadata.unit = UNIT
    item.common_metadata.providers = PROVIDERS
    item.common_metadata.license = "proprietary"

    parts = os.path.basename(cog_href).split("_")
    title = parts[1]

    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = EPSG
    item_projection.wkt2 = CRS_WKT
    item_projection.transform = transform
    item_projection.shape = shape

    cog_asset = Asset(
        href=cog_href,
        title=title,
        description=None,
        media_type=MediaType.COG,
        roles=["data"],
    )
    item.add_asset("data", cog_asset)

    cog_asset_file = FileExtension.ext(cog_asset, add_if_missing=True)
    with fsspec.open(cog_access_href) as file:
        size = file.size
        if size is not None:
            cog_asset_file.size = size

    cog_asset_raster = RasterExtension.ext(cog_asset, add_if_missing=True)
    cog_asset_raster.bands = [
        RasterBand.create(
            nodata=NO_DATA,
            sampling=Sampling.AREA,
            data_type=DataType.FLOAT32,
            spatial_resolution=SPATIAL_RESOLUTION,
        )
    ]

    cog_asset_projection = ProjectionExtension.ext(cog_asset,
                                                   add_if_missing=True)
    cog_asset_projection.epsg = item_projection.epsg
    cog_asset_projection.wkt2 = item_projection.wkt2
    cog_asset_projection.bbox = item_projection.bbox
    cog_asset_projection.transform = item_projection.transform
    cog_asset_projection.shape = item_projection.shape

    return item
