import logging
import os
from datetime import datetime
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
    COLLECTION_TITLE,
    CRS_WKT,
    DESCRIPTION,
    EPSG,
    LICENSE,
    LICENSE_LINK,
    NO_DATA,
    PROVIDERS,
    SPATIAL_EXTENT,
    SPATIAL_RESOLUTION,
    TEMPORAL_EXTENT,
    THUMBNAIL_HREF,
)

logger = logging.getLogger(__name__)


def create_collection() -> Collection:

    collection = Collection(
        id=COLLECTION_ID,
        title=COLLECTION_TITLE,
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
        "data":
        AssetDefinition({
            "type":
            MediaType.COG,
            "roles": ["data"],
            "raster:bands": [
                RasterBand.create(
                    nodata=NO_DATA,
                    sampling=Sampling.AREA,
                    data_type=DataType.FLOAT32,
                    spatial_resolution=SPATIAL_RESOLUTION,
                ).to_dict()
            ],
            "proj:epsg":
            collection_proj.epsg[0],
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

        tags = dataset.tags()
        if "AREA_OR_POINT" in tags:
            if tags["AREA_OR_POINT"] == "Area":
                sampling = Sampling.AREA
            elif tags["AREA_OR_POINT"] == "Point":
                sampling = Sampling.POINT
            else:
                raise ValueError(
                    f"Unknown sampling type {tags['AREA_OR_POINT']}")
        else:
            logger.info(
                "Could not load sampling type from COG. Assuming 'Area'")
            sampling = Sampling.AREA
        if "YEAR" in tags:
            year = int(tags["YEAR"])
        else:
            raise ValueError(
                "Year of collection could not be ascertained from COG.")

    item = Item(
        id=os.path.basename(cog_href).replace(".tif", ""),
        geometry=geometry,
        bbox=bbox,  # TODO: this bbox should be in 4326
        datetime=datetime(year, 1, 1),
        properties={},
        stac_extensions=[],
    )

    item.common_metadata.providers = PROVIDERS
    item.common_metadata.license = "proprietary"

    parts = os.path.basename(cog_href).split("_")
    title = f"BCGS Tile {parts[1]}"

    item_projection = ProjectionExtension.ext(item, add_if_missing=True)
    item_projection.epsg = EPSG
    item_projection.wkt2 = CRS_WKT
    item_projection.bbox = bbox
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
            sampling=sampling,
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
