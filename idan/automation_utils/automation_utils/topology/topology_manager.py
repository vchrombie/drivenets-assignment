import json
import typing
import itertools

import configargparse
from automation_utils.common.exceptions import (
    FileExceptions,
    TopologyException,
)
from automation_utils.inventory_manager import InventoryManager
from automation_utils.common.general.python_helpers import Singleton
import orbital.common as common

from . import topology_data

logger = common.get_logger(__file__)

DEFAULT_CONFIG_FILES = [
    "/etc/orbital/automation_utils.conf",
    "~/.config/orbital/automation_utils.conf",
]

configargparser = configargparse.ArgParser(
    default_config_files=DEFAULT_CONFIG_FILES
)


InterfacesByDevice = typing.Tuple[
    list[topology_data.Lag],
    list[topology_data.Port],
    list[topology_data.Loopback],
]


class TopologyManager(metaclass=Singleton):
    """
    Class used to represent the topology configuration corresponding to the configuration file
    """

    def __init__(self):
        self.inventory_data: topology_data.Inventory = None
        self.inventory_manager: InventoryManager = InventoryManager()

    def load(self, topology_file: str) -> topology_data.Inventory:
        try:
            with open(topology_file) as reader:
                self.inventory_data = json.load(
                    reader, object_hook=topology_data.deserialization_hook
                )
        except FileExceptions as e:
            self.inventory_data = None
            raise TopologyException(
                f"Error reading topology configuration file {topology_file}"
            ) from e
    
    def get_interfaces(self, device_name: str) -> InterfacesByDevice:
        """
        Returns a Tuple of
         - Lag interfaces, from network/sites/devices/lags
         - Port interfaces having "bundle_member" set to "false", from network/sites/devices/ports
         - Loopback interfaces from network/sites/devices/loopbacks
        matching a device by device_name
        param: device_name: string representing the device name
        """

        def get_device_data(
            device_data: str, iterable: typing.Iterable[topology_data.Device]
        ):
            return list(
                itertools.chain.from_iterable(
                    device[device_data] for device in iterable
                )
            )

        devices: list[topology_data.Device] = [
            device
            for device in (
                self._get_element_based_on_path(
                    "network/sites/devices", raise_exc_on_failure=False
                )
                or list()
            )
            if device["name"] == device_name
        ]

        lags: list[topology_data.Lag] = get_device_data("lags", devices)
        ports: list[topology_data.Port] = get_device_data("ports", devices)
        # ports = [port for port in ports if port["bundle-member"] is False]
        loopbacks: list[topology_data.Loopback] = get_device_data(
            "loopbacks", devices
        )
        return (
            lags,
            ports,
            loopbacks,
        )

    def get_peer_interface(
        self, device_name: str, interface_name: str
    ) -> tuple[str, str]:
        """
        Searches TopologyL2L3 for a device corresponding to :py:data: `device_name`
        If it finds one and one end of the p2p link equals :py:data: `interface_name`, this function return the interface name of the other end of the link
        :returns: a tuple of (other_device, other_interface); if present, the string represents the peer device name andinterface name
        """
        expected_topology: list[topology_data.TopologyL2L3] = (
            self.get_expected_topology()
        )
        for topology in expected_topology:
            other_device, other_interface = self._get_other_interface(
                device_name, interface_name, topology, our_side="a"
            )
            if other_interface is not None:
                return other_device, other_interface
            other_device, other_interface = self._get_other_interface(
                device_name, interface_name, topology, our_side="z"
            )
            if other_interface is not None:
                return other_device, other_interface

        return None, None

    def _get_other_interface(
        self,
        device_name: str,
        interface_name: str,
        topology: topology_data.TopologyL2L3,
        our_side: str,
    ) -> tuple[str, str]:
        our_device: str = topology["a"]
        our_interface_name: str = topology["a_interface"]
        other_device: str = topology["z"]
        other_interface: str = topology["z_interface"]
        if our_side == "z":
            our_device: str = topology["z"]
            our_interface_name: str = topology["z_interface"]
            other_device: str = topology["a"]
            other_interface: str = topology["a_interface"]
        if device_name != our_device:
            return None, None
        if interface_name != our_interface_name:
            return None, None
        return other_device, other_interface

    def _get_device_by_name(
        self, device_name: str, all_devices: list[topology_data.Device]
    ) -> list[topology_data.Device]:
        return [
            device for device in all_devices if device["name"] == device_name
        ]

    def get_expected_topology(self) -> list[topology_data.TopologyL2L3]:
        """
        retrieves the links under `topology-l2l3` block in topology configuration data
        """
        paths: str = "network/topology-l2l3"
        return self._get_element_based_on_path(paths)

    def _get_element_based_on_path(
        self, paths: str, raise_exc_on_failure=True, prefix="", root_=None
    ):
        """
        Retrieves the JSON data from the topology file
        parameter: paths: a string representing the path in the JSON file to the data of interest
        parameter: raise_exc_on_failure boolean indicating wether exception should be raised if the path does not exist
                   when raise_exc_on_failure is False this function returns None

        The following parameters are used only for the scope of invoking this function recursively and should not be explicitly set by
         - prefix: a prefix of paths that is used for logging errors when that prefix is not found
         - root_: root node which will be traversed
        """

        def split(path):
            return [e for e in path.split("/") if e]

        root: dict = root_ or self.inventory_data
        paths = paths.strip("/")
        for path in split(paths):
            if isinstance(root, list):
                remaining_path: str = paths.removeprefix(prefix.strip("/"))
                lst = list()
                for root_item in root:
                    inner_element = self._get_element_based_on_path(
                        paths=remaining_path,
                        raise_exc_on_failure=raise_exc_on_failure,
                        prefix=prefix,
                        root_=root_item,
                    )
                    if inner_element is None:
                        continue
                    if isinstance(inner_element, list):
                        lst.extend(inner_element)
                    else:
                        lst.append(inner_element)
                if not lst:
                    return
                return lst

            if path not in root.keys():
                if raise_exc_on_failure is False:
                    return
                raise TopologyException(
                    f"get_expected_topology failed: could not find path {prefix} in topology data"
                )
            prefix += path + "/"
            root = root[path]
        return root

    def validate_topology(self, validation_types=None):
        # the import is done here to avoid circular imports
        from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorRegistry
        from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType

        if not validation_types:
            validation_types = [
                TopologyValidationType.SYSTEM_STATUS,
                TopologyValidationType.INTERFACES_STATUS,
                TopologyValidationType.LLDP_NEIGHBORS,
                TopologyValidationType.PIM_INTERFACES,
                TopologyValidationType.ISIS_NEIGHBORS,
                TopologyValidationType.BGP_NEIGHBORS,
            ]
        
        all_devices = self.inventory_manager.devices
        for device in all_devices:
            for validation_type in validation_types:
                TopologyValidatorRegistry.get_validator(validation_type,
                                                        all_devices[device].vendor).validate(
                    device
                )
