import sys
import json
from pathlib import Path

import yaml
from automation_utils.otg_client.otg_api_client import OtgApiClient

from orbital import common as orbital_common
logger = orbital_common.get_logger(__file__)


class OtgConfigurator:
    def __init__(
        self, name: str, base_url: str, port: int, config_path: str = None
    ):
        self.name = name
        self.base_url = f"{base_url}:{port}"
        if config_path is None:
            self.config_path = "/config"
        # Authentication provider URL. Maybe will be populated from module arguments
        self.auth_url = None

    @staticmethod
    def _load_yaml_file_from_disk(file_path: str):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    @staticmethod
    def _handle_yaml_parsing_exception(
        exc: yaml.YAMLError, file_path: str
    ) -> str:
        logger.error(
            f"[_handle_yaml_parsing_exception] Error while parsing YAML file: {file_path}"
        )
        if hasattr(exc, "problem_mark"):
            if exc.context != None:
                return f"parser says:\n {exc.problem_mark}\n   {str(exc.problem)}  {str(exc.context)}\n   Please correct data and retry"
            else:
                return f"parser says:\n {str(exc.problem_mark)}\n   {str(exc.problem)}\n   Please correct data and retry"
        else:
            return "Something went wrong while parsing yaml file"

    def post_config(self, path_to_yaml_file: str | Path) -> bool:
        try:
            body_json = self._load_yaml_file_from_disk(path_to_yaml_file)
            client = OtgApiClient(self.base_url)
            response = client.send_config_request(
                "POST", self.config_path, body_json
            )
            if response is not None:
                logger.info(
                    "[post_config] Response from API:",
                    json.dumps(response, indent=4),
                )
                return True
            logger.error("[post_config] Failed to get a response from the API")
            return False
        except ValueError as e:
            logger.error(f"[post_config] Error - {e}")
            return False
        except FileNotFoundError:
            logger.error(
                f"[post_config] Error: Config file not found at path - '{path_to_yaml_file}'"
            )
            return False
        except yaml.YAMLError as e:
            logger.error(
                f"[post_config] {self._handle_yaml_parsing_exception(e, path_to_yaml_file)}"
            )
            return False

    def getConfig(self):
        try:
            client = OtgApiClient(self.base_url)
            response = client.send_config_request("GET", self.config_path)
            if response is not None:
                logger.info(
                    "[post_config] Response from API:",
                    json.dumps(response, indent=4),
                )
                return True
            logger.error("[post_config] Failed to get a response from the API")
            return False
        except ValueError as e:
            logger.error(
                f"[post_config] Error during initiation of the OtgApiClient - {e}"
            )
            return False


def main():
    configurator = OtgConfigurator(
        "test_configurator", sys.argv[1], sys.argv[2]
    )
    configurator.post_config(configurator, sys.argv[3])


# Run the module as script to verify it works
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            f"Invalid system arguments {sys.argv}. Usage: python otd_configurator.py <otd_url> <otd_port> <path_to_yaml_file>"
        )
        sys.exit(1)
    main()
