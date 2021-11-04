import logging
import os
import fsspec
import pystac
import pytz
import rasterio
from typing import Optional
from pystac.extensions.version import VersionExtension
from shapely.geometry import mapping, box
from datetime import datetime, timezone
from stactools.core.io import ReadHrefModifier

from pystac import (Asset, CatalogType, Collection, Extent, Item, MediaType,
                    Provider, ProviderRole, SpatialExtent, TemporalExtent)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import (LabelClasses, LabelExtension, LabelTask,
                                     LabelType)
from pystac.extensions.raster import (DataType, RasterBand, RasterExtension,
                                      Sampling)

from stactools.bc_dem.constants import (BCDEM_ID, BCDEM_EPSG,
                                          BCDEM_CRS,LICENSE,DEM_link, LICENSE_LINK,SPATIAL_EXTENT,TEMPORAL_EXTENT,TILING_PIXEL_SIZE,THUMBNAIL_HREF,DESCRIPTION, TITLE, DEM_PROVIDER,BCDEM_Resolution,Unit)


logger = logging.getLogger(__name__)


def create_collection() -> Collection:
    
    providers = [
        Provider(
            name="Province of British Columbia",
            roles=[
                ProviderRole.PRODUCER, ProviderRole.PROCESSOR,
                ProviderRole.HOST
            ],
            url="https://governmentofbc.maps.arcgis.com/apps/MapSeries/index.html?appid=d06b37979b0c4709b7fcf2a1ed458e03",
        )
    ]



    extent = Extent(
        SpatialExtent([SPATIAL_EXTENT]),
        TemporalExtent(TEMPORAL_EXTENT),
    )

    collection = Collection(
        id=BCDEM_ID,
        title=TITLE,
        description=DESCRIPTION,
        license=LICENSE,
        providers=[DEM_PROVIDER],
        extent=extent,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )
 # version extension
    collection_version = VersionExtension.ext(collection, add_if_missing=True)
    collection_proj = ProjectionExtension.summaries(collection,
                                                    add_if_missing=True)
    collection_proj.epsg = [BCDEM_EPSG]

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
                                 data_type=DataType.UINT8
                                 ).to_dict()
           ],
            "proj:epsg":
            collection_proj.epsg[0]
        }),
    }
    
    collection.add_link(LICENSE_LINK)

    return collection     


def create_item(cog_href: str,
                cog_read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    
  if cog_read_href_modifier:
        modified_href = cog_read_href_modifier(cog_href)
  else:
        modified_href = cog_href
        
  with rasterio.open(modified_href) as dataset:
        bbox = list(dataset.bounds)
        geometry = mapping(box(*bbox))
        transform = dataset.transform
        shape = dataset.shape
        size=dataset.size
  item = Item(id=os.path.splitext(os.path.basename(cog_href))[0],
                geometry=geometry,
                bbox=bbox,
                size=size,
                properties={},
                stac_extensions={})

  item.add_links(DEM_link)
  item.common_metadata.resolution = BCDEM_Resolution
  item.common_metadata.Unit =Unit
  item.common_metadata.providers = DEM_PROVIDER
  item.common_metadata.license = "proprietary"
  
  parts = os.path.basename(cog_href).split("_")
  if len(parts) != 4:
        raise ValueError(
            f"Unexpected file name, expected four underscores in name: {os.path.basename(cog_href)}"
        )
  title = parts[1]
  item.add_asset(
        "data",
        Asset(href=cog_href,
              title=title,
              description=None,
              media_type=MediaType.COG,
              roles=["data"]))

  projection = ProjectionExtension.ext(item, add_if_missing=True)
  projection.epsg = BCDEM_EPSG
  projection.transform = transform[0:6]
  projection.shape = shape

  return item
