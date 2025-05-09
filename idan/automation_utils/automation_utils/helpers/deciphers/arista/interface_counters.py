import json

from automation_utils.data_objects.interface_counters import InterfaceCounters
from automation_utils.helpers.deciphers.decipher_base import Decipher


class InterfaceCountersDecipher(Decipher):
    @staticmethod
    def _bps_to_mbps(bps: float) -> float:
        """Convert bits per second to megabits per second"""
        return bps * 8 / (1000 * 1000)  # Convert Bps to Mbps

    @staticmethod
    def decipher(cli_response: str) -> dict:
        # Parse the JSON string into a Python dictionary
        data = json.loads(cli_response)

        # Initialize result dictionary
        counters_dict = {}

        # Iterate over each interface entry
        for interface_name, interface_data in data.get(
            "interfaces", {}
        ).items():
            # Convert rates from Bps to Mbps
            rx_mbps = InterfaceCountersDecipher._bps_to_mbps(
                interface_data["inBpsRate"]
            )
            tx_mbps = InterfaceCountersDecipher._bps_to_mbps(
                interface_data["outBpsRate"]
            )

            # Create InterfaceCounters object
            counter = InterfaceCounters(
                interface_name=interface_name, rx_mbps=rx_mbps, tx_mbps=tx_mbps
            )
            counters_dict[interface_name] = counter

        return counters_dict
