import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def inspect_file(filepath_str):
    """Return basic information about an existing file."""
    path = Path(filepath_str)

    if not path.is_file():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")
    
    return {"name": path.name, "extension": path.suffix}


def inspect_extension(file_info):
    """Confirm that the file uses a supported text extension."""
    supported_extension = ".txt"

    if file_info["extension"] != supported_extension:
        logger.error(f"Unsupported text format: {file_info["extension"]}")
        raise ValueError(f"Unsupported text format: {file_info["extension"]}")

    return file_info
