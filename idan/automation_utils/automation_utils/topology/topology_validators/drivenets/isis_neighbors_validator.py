import orbital.common as common
from automation_utils.helpers.deciphers.drivenets.isis_neighbors import IsisConfigDecipher, IsisNeighborsDecipher
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)


@TopologyValidatorRegistry.register_validator(TopologyValidationType.ISIS_NEIGHBORS, Vendors.DRIVENETS)
class IsisNeighborsValidator(TopologyValidatorBase):
    def validate(self,
                 device: str, 
                 **kwargs):
        logger.debug(f"\n\nValidating ISIS neighbors for {device}")
        isis_interfaces = self.device_manager.cli_sessions[device].send_command(
            command="show config protocols isis", 
            decipher=IsisConfigDecipher
        )
        # isis_interfaces is a dictionary of the configured Isis bundle interfaces.


        """
        Instance 33287:
        System Id                      Interface               Level  State         Last State Change    Holdtime  SNPA
        edge01                         bundle-217              L2     Up            2h5m47s              25        point-to-point
        tcr01.siteA.cran1              bundle-343              L2     Up            1h46m29s             22        point-to-point
        tcr02.siteA.cran1              bundle-340              L2     Up            1h44m13s             23        point-to-point
        """
        isis_neighbors = self.device_manager.cli_sessions[device].send_command(
            command="show isis neighbors", 
            decipher=IsisNeighborsDecipher
        )

        for neighbor in isis_neighbors.neighbors:
            assert neighbor in isis_interfaces, f"{device} - Interface: {neighbor} not found  in configured ISIS interfaces"
            assert isis_neighbors.neighbors[neighbor].state == "Up", f"{device} - Interface: {neighbor} - ISIS neighbor state is not Up"
            assert isis_neighbors.neighbors[neighbor].last_change, f"{device} - Interface: {neighbor} - ISIS neighbor last change is empty"
            peer_device, peer_interface = self.topology_manager.get_peer_interface(device, neighbor)
            assert peer_device is not None, f"{device} - Interface: {neighbor} - peer device is not found in topology"
            assert isis_neighbors.neighbors[neighbor].system_name == peer_device, f"{device} - Interface: {neighbor} - ISIS neighbor system name is not {peer_device}"
            logger.debug(f"{device} - Interface: {neighbor} - ISIS neighbors check passed")
        logger.debug(f"{device}: ISIS neighbors check passed")



