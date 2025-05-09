from automation_utils.device import Device
from automation_utils.cli.cli_ios import CliIos
from automation_utils.cli.cli_ceos import CliCeos
from automation_utils.cli.cli_dnos import CliDnos
from automation_utils.otg_client.otg_api_client import OtgApiClient
from automation_utils.common.general.python_helpers import Singleton

import orbital.common as common

logger = common.get_logger(__file__)


class DeviceManager(metaclass=Singleton):
    def __init__(self):
        self.cli_sessions = {}
        self.otg_devices = {}

    def init_devices(self, devices: dict[str, Device]) -> None:
        self.cli_sessions = {}
        self.otg_devices = {}
        for device_name, device in devices.items():
            if not device.vendor:
                raise ValueError(
                    f"Device vendor is mandatory for device {device.hostname}"
                )
            if device.vendor.lower() == "drivenets":
                self.cli_sessions[device_name] = CliDnos(
                    device.hostname, device.username, device.password
                )
            elif device.vendor.lower() == "arista":
                self.cli_sessions[device_name] = CliCeos(
                    device.hostname, device.username, device.password
                )
            elif device.vendor.lower() == "cisco":
                self.cli_sessions[device_name] = CliIos(
                    device.hostname, device.username, device.password
                )
            elif device.vendor.lower() == "ixia":
                self.otg_devices[device_name] = OtgApiClient(
                    name=device_name,
                    base_url=f"https://{device.hostname}",
                    port=int(device.port),
                )
            else:
                raise ValueError(
                    f"Unsupported vendor '{device.vendor}' for device {device_name}"
                )
