from automation_utils.common import exceptions
import orbital.common as common
from automation_utils.data_objects.bgp_summary import BgpSummary
from automation_utils.data_objects.config_protocols_bgp import ConfigProtocolsBgp
from automation_utils.helpers.deciphers.drivenets.bgp_summary import (
    BgpSummaryIpv4Decipher as DnosBgpIpv4Decipher,
)
from automation_utils.helpers.deciphers.drivenets.show_config_protocols_bgp import ShowConfigProtocolsBgpDecipher
from automation_utils.ssh_client import consts
from automation_utils.topology.topology_validators.topology_validator import TopologyValidatorBase, TopologyValidatorRegistry
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors

logger = common.get_logger(__file__)



@TopologyValidatorRegistry.register_validator(TopologyValidationType.BGP_NEIGHBORS, Vendors.DRIVENETS)
class BgpNeighborsValidator(TopologyValidatorBase):
    def validate(self,
                 device: str,
                 **kwargs):
        bgp_summary: BgpSummary = BgpSummary(None, None, {})
        try:
            logger.debug(f"\n\nValidating BGP neighbors for {device}")
            bgp_summary: BgpSummary = self.device_manager.cli_sessions[device].send_command(
                command = "show bgp summary",
                decipher = DnosBgpIpv4Decipher
            )
        # When we gotempty cli_response we assume that BGP is not configured on the device and skip validation
        except exceptions.UnexpectedOutput as e:
            if e.args[0] == consts.NO_OUTPUT_EXCEPTION_MSG:
                logger.debug(f"{device}: Caught 'UnexpectedOutput' exception. We assume no BGP configured on the device, skipping")
                return
        # bgp_summary is a dictionary of the asn number, bgp_identifier and bgp_neighbors

        assert bgp_summary.as_number, f"{device}: Device asn: {bgp_summary.as_number} is invalid"
        assert bgp_summary.bgp_router_identifier, f"{device}: Device bgp router identifier: {bgp_summary.bgp_router_identifier} is invalid"

        config_protocols_bgp: ConfigProtocolsBgp = self.device_manager.cli_sessions[device].send_command(
            command=f"show config protocols bgp {bgp_summary.as_number} | inc neighbor",
            decipher=ShowConfigProtocolsBgpDecipher
        )
        # config_protocols_bgp is a list of the neighbors_ip_addresses

        for neighbor in config_protocols_bgp.neighbors_ip_addresses:
            assert neighbor in bgp_summary.neighbors, f"{device} - Interface: {neighbor} not found  in configured BGP interfaces"
            assert bgp_summary.neighbors[neighbor].up_down_time, f"{device} - Interface: {neighbor} - BGP neighbor up_down_time is empty"
            assert bgp_summary.neighbors[neighbor].up_down_time != "never", f"{device} - Interface: {neighbor} - BGP neighbor up_down_time is equal 'never"
            # TODO: check empty string option
            if bgp_summary.neighbors[neighbor].state_pfx_accepted is int:
                assert bgp_summary.neighbors[neighbor].state_pfx_accepted >= 0, f"{device} - Neighbor: {neighbor} - BGP neighbor state_pfx_accepted is less then 0"
            logger.debug(f"{device} - Neighbor: {neighbor} - BGP neighbors check passed")
        logger.debug(f"{device}: BGP neighbors check passed")
