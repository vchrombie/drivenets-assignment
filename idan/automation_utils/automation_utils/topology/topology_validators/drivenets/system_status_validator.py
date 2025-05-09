import orbital.common as common
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.helpers.deciphers.drivenets.system_status import SystemStatusDecipher
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)

@TopologyValidatorRegistry.register_validator(TopologyValidationType.SYSTEM_STATUS, Vendors.DRIVENETS)
class SystemStatusValidator(TopologyValidatorBase):
    def validate(self, 
                 device: str, 
                 **kwargs):
        logger.debug(f"\n\nValidating system status for {device}")
        status = self.device_manager.cli_sessions[device].send_command(
            command="show system", 
            decipher=SystemStatusDecipher
        )
        assert status.status['NCC'] == 'active-up', f"{device} - NCC status is not active-up"
        assert status.status['NCP'] == 'up', f"{device} - NCP status is not up"
        logger.debug(f"{device}: system status check passed")
