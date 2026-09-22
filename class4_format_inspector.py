import json
import logging
from pathlib import Path

import pandas as pd
import yaml
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def inspect_csv(filepath):
    """Read a CSV file and display basic information."""
    df = pd.read_csv(filepath)
    logger.info(f"Inspecting CSV: {filepath}")
    print(df.head(3))


def inspect_json(filepath):
    """Read a JSON file and display basic information."""
    with open(filepath, "r") as f:
        data = json.load(f)
        logger.info(f"Inspecting JSON: {filepath}")
    print(data["Status"])
    print(data["Data"])


def inspect_yaml(filepath):
    """Read a YAML file and display basic information."""
    with open(filepath, "r") as f:
        config = yaml.safe_load(f)
        logger.info(f"Inspecting YAML: {filepath}")
    
    print(config["cleaning"]["missing"])
    print(config["processing"]["batch_size"])


def inspect_env():
    """Read a .env file and display basic information."""
    load_dotenv()

    keys = [
        key for key in ["USERNAME", "PASSWORD"]
        if os.getenv(key) is not None
    ]

    logger.info(f"Loaded environment variables from .env")
    print(keys)


def main():
    data_dir = Path('data')
    csv_filepath = data_dir / 'sample.csv'
    json_filepath = data_dir / 'sample.json'
    yaml_filepath = data_dir / 'sample.yaml'

    inspect_csv(csv_filepath)
    inspect_json(json_filepath)
    inspect_yaml(yaml_filepath)
    inspect_env()


if __name__ == "__main__":
    main()