import logging

logger = logging.getLogger(__name__)
import yaml


def get_yaml(yaml_filepath: str) -> dict:
    with open(yaml_filepath) as f:
        return yaml.safe_load(f)
