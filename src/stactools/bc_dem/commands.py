import logging

import click

from stactools.bc_lidar import stac, cog

logger = logging.getLogger(__name__)


def create_bclidar_command(cli):
    """Creates the stactools-bc-lidar command line utility."""
    @cli.group(
        "bclidar",
        short_help=("Commands for working with stactools-bc-lidar"),
    )
    def bclidar():
        pass
    @bclidar.command(
        "create-cog",
        short_help="Creates a COG from a .tif file",
    )
    @click.argument("source")
    @click.argument("destination")
    def create_cog_command(source: str, destination: str) -> None:
        """Creates a COG
        Args:
            source (str): An HREF for the .tif file.
            destination (str): An HREF for the output COG.
        """
        cog.create_cog(source, destination)

        return None

    @bclidar.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    def create_collection_command(destination: str):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

        collection.save_object()

        return None

    @bclidar.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

        return None

    return bclidar
