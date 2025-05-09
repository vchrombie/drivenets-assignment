"""
The devices in the configuration file are a list consisting of Device instance representations
inventory yml example:

devices:
  tcr03:
    hostname: 100.93.118.28
    username: user
    password: password
    vendor: drivenets
  tcr04:
    hostname: 100.93.118.29
    username: user
    password: password
    vendor: drivenets
"""

import yaml
from automation_utils.device import Device
from automation_utils.common.general.python_helpers import Singleton

import orbital.common as common

logger = common.get_logger(__file__)


class InventoryManager(metaclass=Singleton):
    def __init__(self):
        self.devices = {}

    def load(self, file_path):
        """
        load inventory object from yaml file
        """
        try:
            with open(file_path, "r") as f:
                yaml_data = yaml.safe_load(f)
            for key, config in yaml_data.items():
                if key == "devices":
                    for device_name in config:
                        self.devices[device_name] = Device(
                            **config[device_name]
                        )
        except yaml.YAMLError as e:
            logger.error(f"Error parsing inventory: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Error loading inventory: {e}")
            raise
