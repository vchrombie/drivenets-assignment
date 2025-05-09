import logging
import time
import pytest


from automation_utils.helpers.deciphers.drivenets.interface_counters import InterfaceCountersDecipher
from automation_utils.helpers.deciphers.common.ip_route import IpRouteDecipher

from . import conftest


logger = logging.getLogger()

DEVICE_CONFIG_FILE = "tests/automation_utils_test/resources/config_topology_validation.yml"
TOPOLOGY_CONFIG_FILE = "tests/automation_utils_test/resources/test_topology_validation_topology.json"


ASBR01 = 'asbr01.siteA.cran1'
ASBR02 = 'asbr02.siteA.cran1'
TCR01 = 'tcr01.siteA.cran1'
TCR02 = 'tcr02.siteA.cran1'

ALL_DEVICES = [ASBR01, ASBR02, TCR01, TCR02]
EDGE02_LOOPBACK_IP = '40.40.40.40/32'
TCR01_BUNDLE_NAME = 'bundle-343'
TCR02_BUNDLE_NAME = 'bundle-340'


# edge01# run ping 40.40.40.40 source-interface lo0 count 1000000 interval 0.001 size 65507
# expected rate per second: 228 Mbps
EXPECTED_RATE_PER_SECOND = 228


class TestEcmp:
    def _validate_traffic_rate(self, rate, expected_rate):
        threshold_tolerance = expected_rate * 0.1
        assert abs(rate - expected_rate) <= threshold_tolerance, \
            f"The traffic rate is not within 10% of expected rate {expected_rate} Mbps"

    @pytest.mark.parametrize(
        [conftest.DEVICE_CONFIG, conftest.TOPOLOGY_CONFIG],
        [(DEVICE_CONFIG_FILE, TOPOLOGY_CONFIG_FILE)],
        indirect=True
    )
    def test_ecmp(self, device_manager, topology_manager):
        logger.info("\n\nValidating topology")
        topology_manager.validate_topology()
 
        logger.info("\n\nValidating traffic is flowing via both interfaces")
        ip_routes = device_manager.cli_sessions[ASBR01].send_command(
            command=f"show route {EDGE02_LOOPBACK_IP}",
            decipher=IpRouteDecipher
        )

        ip_route_interfaces = [next_hop.interface for next_hop in ip_routes.next_hops]
        assert TCR01_BUNDLE_NAME in ip_route_interfaces
        assert TCR02_BUNDLE_NAME in ip_route_interfaces

        logger.debug(f"\n\nMeasuring current interfaces counters for {ASBR01}:")
        interfaces_counters = device_manager.cli_sessions[ASBR01].send_command(
            command="show interfaces counters",
            decipher=InterfaceCountersDecipher
        )

        logger.debug(f"\n\nVerify that traffic is flowing")
        for rate in ['rx_mbps', 'tx_mbps']:
            # aggregate rate from both interfaces
            self._validate_traffic_rate(getattr(interfaces_counters[TCR01_BUNDLE_NAME], rate) +
                                      getattr(interfaces_counters[TCR02_BUNDLE_NAME], rate),
                                      EXPECTED_RATE_PER_SECOND)

        # disable one of the interfaces
        logger.info(f"\n\nDisabling {TCR01_BUNDLE_NAME} that connects {ASBR01} to {TCR01}...")
        device_manager.cli_sessions[ASBR01].edit_config(f"interfaces {TCR01_BUNDLE_NAME} admin-state disabled")

        logger.info(f"\n\nWait 30 seconds for traffic to stabilize...")
        time.sleep(30)

        logger.info("\n\nValidating traffic is flowing via one interface")
        ip_routes = device_manager.cli_sessions[ASBR01].send_command(
            command=f"show route {EDGE02_LOOPBACK_IP}",
            decipher=IpRouteDecipher
        )

        ip_route_interfaces = [next_hop.interface for next_hop in ip_routes.next_hops]
        assert TCR01_BUNDLE_NAME not in ip_route_interfaces
        assert TCR02_BUNDLE_NAME in ip_route_interfaces

        logger.debug(f"\n\nMeasuring current interfaces counters for {ASBR01}:")
        interfaces_counters = device_manager.cli_sessions[ASBR01].send_command(
            command="show interfaces counters", 
            decipher=InterfaceCountersDecipher
        )

        logger.debug(f"\n\nVerify that traffic is flowing through {TCR02_BUNDLE_NAME}")
        for rate in ['rx_mbps', 'tx_mbps']:
            self._validate_traffic_rate(getattr(interfaces_counters[TCR02_BUNDLE_NAME], rate),
                                      EXPECTED_RATE_PER_SECOND)
        # restore the bundle
        logger.info(f"\n\nRestoring {TCR01_BUNDLE_NAME} that connects {ASBR01} to {TCR01}...")
        device_manager.cli_sessions[ASBR01].edit_config(f"interfaces {TCR01_BUNDLE_NAME} admin-state enabled")
        logger.info(f"\n\nWait 10 seconds for traffic to stabilize...")
        time.sleep(10)

        logger.info("\n\nValidating traffic is flowing via both interfaces")
        ip_routes = device_manager.cli_sessions[ASBR01].send_command(
            command=f"show route {EDGE02_LOOPBACK_IP}",
            decipher=IpRouteDecipher
        )

        ip_route_interfaces = [next_hop.interface for next_hop in ip_routes.next_hops]
        assert TCR01_BUNDLE_NAME in ip_route_interfaces
        assert TCR02_BUNDLE_NAME in ip_route_interfaces

