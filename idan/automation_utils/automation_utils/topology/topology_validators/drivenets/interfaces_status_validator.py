import orbital.common as common
from automation_utils.helpers.deciphers.drivenets.interface_status import InterfacesStatusDecipher as DnosInterfacesStatusDecipher
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)


@TopologyValidatorRegistry.register_validator(TopologyValidationType.INTERFACES_STATUS, Vendors.DRIVENETS)
class InterfacesStatusValidator(TopologyValidatorBase):
    def validate(self, 
                 device: str, 
                 **kwargs):
            logger.debug(f"\n\nValidating interfaces status for {device}")
            interfaces_status = self.device_manager.cli_sessions[device].send_command(
                command="show interfaces", 
                decipher=DnosInterfacesStatusDecipher
            )
            lags, ports, loopbacks = self.topology_manager.get_interfaces(device)
            for lag in lags:
                assert interfaces_status[lag["interface-id"]].operational_status == "up", f"Device: {device} - Interface: {lag['interface-id']} operational status is not up"
                assert interfaces_status[lag["interface-id"]].admin_status == "enabled", f"Device: {device} - Interface: {lag['interface-id']} admin status is not enabled"
                logger.debug(f"Device: {device} - Interface: {lag['interface-id']} status check passed")
            for port in ports:
                assert interfaces_status[port["interface-id"]].operational_status == "up"
                assert interfaces_status[port["interface-id"]].admin_status == "enabled", f"Device: {device} - Interface: {port['interface-id']} admin status is not enabled"
                logger.debug(f"Device: {device} - Interface: {port['interface-id']} status check passed")
            for loopback in loopbacks:
                assert interfaces_status[loopback["interface-id"]].operational_status == "up", f"Device: {device} - Interface: {loopback['interface-id']} operational status is not up"
                assert interfaces_status[loopback["interface-id"]].admin_status == "enabled", f"Device: {device} - Interface: {loopback['interface-id']} admin status is not enabled"
                logger.debug(f"Device: {device} - Interface: {loopback['interface-id']} status check passed")
            logger.debug(f"{device}: interfaces status check passed")
