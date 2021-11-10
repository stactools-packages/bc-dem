# flake8: noqa

from datetime import datetime

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

COLLECTION_ID = "bc-dem"
COLLECTION_TITLE = 'LidarBC DEM'
EPSG = 3157
CRS_WKT = CRS.from_epsg(EPSG).to_wkt()
SPATIAL_RESOLUTION = 1  # Are we sure about this value? The spacing is 1, which may not be the same thing.
LICENSE = "proprietary"
LICENSE_URL = "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc"
LICENSE_LINK = Link(rel="license",
                    target=LICENSE_URL,
                    title="Open Government Licence - British Columbia")
SPATIAL_EXTENT = [
    0.0,
    0.0,
    0.0,
    0.0,
]  # TODO: Figure out the total extent of the collection
TEMPORAL_EXTENT = [datetime(2016, 1, 1) or None, datetime(2019, 12, 31)]
THUMBNAIL_HREF = "https://www.arcgis.com/sharing/rest/content/items/c3bf9d29cc7b44718dca370435353994/resources/ex1_dem__1625007392868.JPG"
DESCRIPTION = """LidarBC's Open LiDAR Data Portal is an initiative to provide open public access to LiDAR and associated datasets collected by the Province of British Columbia. The data presented herein is released as Open Data under the Open Government Licence – British Columbia (OGL-BC).
Digital Elevation Model (DEM) is a derivative product of LiDAR and a representation of the terrain bare earth surface. The bare earth DEM is developed by removing vegetation and structures from the LiDAR data and developed through interpolation of the elevation data."""
PROVIDERS = [
    Provider(
        name="Province of British Columbia",
        roles=[
            ProviderRole.HOST,
            ProviderRole.PROCESSOR,
            ProviderRole.PRODUCER,
        ],
        url=
        "https://governmentofbc.maps.arcgis.com/apps/MapSeries/index.html?appid=d06b37979b0c4709b7fcf2a1ed458e03",
    )
]

NO_DATA = -9999
