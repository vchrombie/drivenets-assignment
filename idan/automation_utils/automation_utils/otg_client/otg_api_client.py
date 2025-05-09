import json
from pathlib import Path

import yaml
import requests
from automation_utils.otg_client.otg_request_sender import OtgRequestSender

import orbital.common as common

logger = common.get_logger(__file__)


class OtgApiClient:
    config_api_path: str = "/config"
    control_state_api_path: str = "/control/state"
    control_action_api_path: str = "/control/action"
    monitor_metrix_api_path: str = "/monitor/metrics"
    monitor_states_api_path: str = "/monitor/states"
    monitor_capture_api_path: str = "/monitor/capture"
    capabilities_version_api_path: str = "/capabilities/version"

    def __init__(self, name: str, base_url: str, port: int):
        self.name = name
        self.base_url = f"{base_url}:{port}"

        # Authentication provider URL. Maybe will be populated from module arguments
        self.auth_url = None

    @staticmethod
    def load_yaml_file_from_disk(file_path: Path | str):
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

    def _change_state_api(
        self,
        method_name: str,
        http_method: str,
        api_path: str,
        path_to_yaml_file: str | Path,
        return_response: bool = False,
    ) -> bool | dict:
        try:
            body_json = self.load_yaml_file_from_disk(path_to_yaml_file)
            client = OtgRequestSender(self.base_url)
            response = client.send_api_request(
                http_method, api_path, body_json
            )
            if response is not None:
                logger.info(
                    f"[{method_name}] Response from API:",
                    json.dumps(response, indent=4),
                )
                return response if return_response else True
            logger.error(
                f"[{method_name}] Failed to get a response from the API"
            )
            return False
        except ValueError as e:
            logger.error(f"[{method_name}] Error - {e}")
            return False
        except FileNotFoundError:
            logger.error(
                f"[{method_name}] Error: Config file not found at path - '{path_to_yaml_file}'"
            )
            return False
        except yaml.YAMLError as e:
            logger.error(
                f"[{method_name}] {self._handle_yaml_parsing_exception(e, path_to_yaml_file)}"
            )
            return False

    def _get_state_api(
        self, method_name: str, http_method: str, api_path: str
    ) -> requests.Response | bool:
        try:
            client = OtgRequestSender(self.base_url)
            response = client.send_api_request(http_method, api_path)
            if response is not None:
                logger.info(
                    f"[{method_name}] Response from API:",
                    json.dumps(response, indent=4),
                )
                return response
            logger.error(
                f"[{method_name}] Failed to get a response from the API"
            )
            return False
        except ValueError as e:
            logger.error(f"[{method_name}] Error - {e}")
            return False

    ##### Cli OTG Api Testing Method #####
    def process_user_input(self, user_input):
        try:
            parts = user_input.split()
            method_name = parts[0]
            args_flag_index = None
            args = None

            # Check if the method arguments specified
            if "-a" in parts:
                args_flag_index = parts.index("-a")
                args = parts[args_flag_index + 1 :]

            # Check if decipher is specified
            decipher_method = None
            if "-d" in parts:
                decipher_flag_index = parts.index("-d")
                decipher_method_name = parts[decipher_flag_index + 1]
                decipher_method = getattr(self, decipher_method_name)
                if decipher_method is None:
                    raise ValueError(
                        f"Unknown decipher method: {decipher_method_name}"
                    )
                if args_flag_index is not None:
                    args = parts[args_flag_index + 1 : decipher_flag_index]

            # Get OTG Api method reference
            method = getattr(self, method_name)
            if method is None:
                raise ValueError(f"Unknown method: {method_name}")

            # Call the OTG Api method
            if args is None:
                result = method()
            else:
                result = method(*args)

            # Apply the Decipher method if specified
            if decipher_method:
                result = decipher_method(result)

            # Output the result
            print(f"Result --->\n {result}")

        except Exception as e:
            print(f"Error: {e}")

    ##### OTG Configuration Methods #####
    def post_otg_config(self, path_to_yaml_file: str | Path) -> bool:
        return self._change_state_api(
            method_name="post_otg_config",
            http_method="POST",
            api_path=OtgApiClient.config_api_path,
            path_to_yaml_file=path_to_yaml_file,
        )

    def get_otg_config(self) -> dict | bool:
        return self._get_state_api(
            method_name="get_otg_config",
            http_method="GET",
            api_path=OtgApiClient.config_api_path,
        )

    def patch_otg_config(self, path_to_yaml_file: str | Path) -> bool:
        return self._change_state_api(
            method_name="patch_otg_config",
            http_method="PATCH",
            api_path=OtgApiClient.config_api_path,
            path_to_yaml_file=path_to_yaml_file,
        )

    ##### OTG Control Methods #####
    def post_otg_control_state(self, path_to_yaml_file: str | Path) -> bool:
        return self._change_state_api(
            method_name="post_otg_control_state",
            http_method="POST",
            api_path=OtgApiClient.control_state_api_path,
            path_to_yaml_file=path_to_yaml_file,
        )

    def post_otg_control_action(self, path_to_yaml_file: str | Path) -> bool:
        return self._change_state_api(
            method_name="post_otg_control_action",
            http_method="POST",
            api_path=OtgApiClient.control_action_api_path,
            path_to_yaml_file=path_to_yaml_file,
        )

    ##### OTG Monitor Methods #####
    def post_otg_monitor_metrics(
        self, path_to_yaml_file: str | Path
    ) -> dict | bool:
        return self._change_state_api(
            method_name="post_otg_monitor_metrics",
            http_method="POST",
            api_path=OtgApiClient.monitor_metrix_api_path,
            path_to_yaml_file=path_to_yaml_file,
            return_response=True,
        )

    def post_otg_monitor_states(
        self, path_to_yaml_file: str | Path
    ) -> dict | bool:
        return self._change_state_api(
            method_name="post_otg_monitor_states",
            http_method="POST",
            api_path=OtgApiClient.monitor_states_api_path,
            path_to_yaml_file=path_to_yaml_file,
            return_response=True,
        )

    def post_otg_monitor_capture(self, path_to_yaml_file: str | Path) -> bool:
        return self._change_state_api(
            method_name="post_otg_monitor_capture",
            http_method="POST",
            api_path=OtgApiClient.monitor_capture_api_path,
            path_to_yaml_file=path_to_yaml_file,
        )

    ##### OTG Capabilities Methods #####
    def get_otg_capabilities_version(self) -> dict | bool:
        return self._get_state_api(
            method_name="get_otg_capabilities_version",
            http_method="GET",
            api_path=OtgApiClient.capabilities_version_api_path,
        )
