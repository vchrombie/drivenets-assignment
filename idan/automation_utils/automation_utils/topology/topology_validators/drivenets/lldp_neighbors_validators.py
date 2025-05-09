import orbital.common as common
from automation_utils.helpers.deciphers.drivenets.lldp_neighbors import LldpNeighborsDecipher as DnosLldpDecipher
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)


@TopologyValidatorRegistry.register_validator(TopologyValidationType.LLDP_NEIGHBORS, Vendors.DRIVENETS)
class LldpNeighborsValidator(TopologyValidatorBase):
    def validate(self,
                 device: str, 
                 **kwargs):
        logger.debug(f"\n\nValidating LLDP neighbors for {device}")
        lldp_neighbors = self.device_manager.cli_sessions[device].send_command(
            command="show lldp neighbors", 
            decipher=DnosLldpDecipher
        )

        _, ports, _ = self.topology_manager.get_interfaces(device)
        for port in ports:
            port_name = port["interface-id"]
            peer_device, peer_interface = self.topology_manager.get_peer_interface(device, port_name)
            if peer_interface:
                logger.debug(f"Expected peer for {port_name}: {peer_device}: {peer_interface}")
                lldp_neighbor = lldp_neighbors.get(peer_interface, None)
                assert lldp_neighbor is not None, f"{device} - Interface: {port_name} - LLDP neighbor is not found"
                assert lldp_neighbor.system_name == peer_device, f"{device} - Interface: {port_name} - LLDP neighbor system name is not {peer_device}"
                assert lldp_neighbor.neighbor_interface == peer_interface, f"{device} - Interface: {port_name} - LLDP neighbor interface is not {peer_interface}"
                logger.debug(f"{device} - Interface: {port_name} - LLDP neighbor check passed")
        logger.debug(f"{device}: LLDP neighbors check passed")
