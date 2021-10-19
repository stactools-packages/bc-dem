from datetime import datetime

from pyproj import CRS
from pystac import Link, Provider, ProviderRole

BCDEM_ID = "BC_DEM"
BCDEM_EPSG = 3157
BCDEM_CRS = CRS.from_epsg(BCDEM_EPSG)
LICENSE = "proprietary"
lic_link = "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc"
LICENSE_LINK = Link(rel="license",
                    target=lic_link,
                    title="Open Government Licence - British Columbia")
SPATIAL_EXTENT = [-130.2, 21.7, -63.7, 49.1]
TEMPORAL_EXTENT = [datetime(2016, 1, 1) or None, datetime(2020, 1, 1)]
SPATIAL_RES = 30
THUMBNAIL_HREF = "https://www.mrlc.gov/sites/default/files/2019-04/Land_cover_L48_6.png"
DESCRIPTION = """The National Land Cover Database (NLCD) is an operational land cover
monitoring program providing updated land cover and related information for the United States at
five-year intervals."""
TITLE = 'NLCD Land Cover (CONUS) All Years'
NLCD_PROVIDER = Provider(
    name="United States Geological Survey",
    roles=[ProviderRole.PRODUCER, ProviderRole.PROCESSOR, ProviderRole.HOST],
    url="https://www.mrlc.gov/data/nlcd-land-cover-conus-all-years")
