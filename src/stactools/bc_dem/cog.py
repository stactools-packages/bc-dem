import logging
from subprocess import CalledProcessError, check_output

logger = logging.getLogger(__name__)


def create_cog(
    input_path: str,
    year: int,
    output_path: str,
) -> str:
    """Create COG from a tif
    Args:
        input_path (str): Path to the Natural Resources Canada Land Cover data.
        output_path (str): The path to which the COG will be written.
        year (str): The year the data was collected.
    Returns:
        str: The path to the output COG.
    """

    output = None
    try:
        cmd = [
            "gdal_translate",
            "-of",
            "COG",
            "-co",
            "NUM_THREADS=ALL_CPUS",
            "-co",
            "BLOCKSIZE=512",
            "-co",
            "compress=deflate",
            "-co",
            "LEVEL=9",
            "-co",
            "PREDICTOR=YES",
            "-co",
            "OVERVIEWS=IGNORE_EXISTING",
            "-mo",
            f"YEAR={year}",
            input_path,
            output_path,
        ]

        try:
            output = check_output(cmd)
        except CalledProcessError as e:
            output = e.output
            raise
        finally:
            logger.info(f"output: {str(output)}")

    except Exception:
        logger.error("Failed to process {}".format(output_path))
        raise

    return output_path
