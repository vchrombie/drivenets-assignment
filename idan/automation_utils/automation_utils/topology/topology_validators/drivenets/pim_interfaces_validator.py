import orbital.common as common
from automation_utils.helpers.deciphers.drivenets.pim_protocol import PimConfigDecipher, PimNeighborsDecipher
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)


@TopologyValidatorRegistry.register_validator(TopologyValidationType.PIM_INTERFACES, Vendors.DRIVENETS)
class PimInterfacesValidator(TopologyValidatorBase):
    def validate(self, 
                 device: str, 
                 **kwargs):
        logger.debug(f"\n\nValidating PIM interfaces for {device}")
        pim_interfaces = self.device_manager.cli_sessions[device].send_command(
            command="show config protocols pim", 
            decipher=PimConfigDecipher
        )
        pim_neighbors = self.device_manager.cli_sessions[device].send_command(
            command="show pim neighbors", 
            decipher=PimNeighborsDecipher
        )
        lags, _, _ = self.topology_manager.get_interfaces(device)
        for lag in pim_interfaces:
            assert lag in pim_neighbors, f"{device} - Interface: {lag} not found in pim neighbors"
            assert next((l for l in lags if l["interface-id"] == lag), None), f"{device} - Interface: {lag} not found in topology"
            assert pim_neighbors[lag].uptime, f"{device} - Interface: {lag} uptime is empty"
            logger.debug(f"{device} - Interface: {lag} PIM interface check passed")
        logger.debug(f"{device}: PIM neighbors check passed")