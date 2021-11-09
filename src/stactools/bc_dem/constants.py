from datetime import datetime
from pyproj import CRS
from pystac import Link, Provider, ProviderRole

BCDEM_ID = "BC_DEM"
BCDEM_EPSG = 3157
BCDEM_Resolution=1
Unit="meters"
BCDEM_CRS = CRS.from_epsg(BCDEM_EPSG)
LICENSE = "proprietary"
DEM_link = "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc"
LICENSE_LINK = Link(rel="license",
                    target=DEM_link,
                    title="Open Government Licence - British Columbia")
SPATIAL_EXTENT = []
START_DATE=datetime(2016, 1, 1)
TEMPORAL_EXTENT = [datetime(2016, 1, 1) or None, datetime(2019, 12, 31)]
TILING_PIXEL_SIZE = (1.000000000000000,-1.000000000000000)
THUMBNAIL_HREF = ""
DESCRIPTION = """LidarBC's Open LiDAR Data Portal is an initiative to provide open public access to LiDAR and associated datasets collected by the Province of British Columbia. The data presented herein is released as Open Data under the Open Government Licence – British Columbia (OGL-BC).
Digital Elevation Model (DEM) is a derivative product of LiDAR and a representation of the terrain bare earth surface. The bare earth DEM is developed by removing vegetation and structures from the LiDAR data and developed through interpolation of the elevation data."""
TITLE = 'LidarBC'
DEM_PROVIDER = Provider(
    name="Province of British Columbia",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
    url="https://governmentofbc.maps.arcgis.com/apps/MapSeries/index.html?appid=d06b37979b0c4709b7fcf2a1ed458e03")
