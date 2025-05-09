import re

from automation_utils.data_objects.bgp_summary import BgpSummary, BgpNeighbor
from automation_utils.helpers.deciphers.decipher_base import Decipher


class BgpSummaryIpv4Decipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> BgpSummary:
        # Initialize variables
        as_number = None
        bgp_router_identifier = None
        neighbors: dict[str: BgpNeighbor] = {}

        # Empty response for 'show bgp summary' command means no BGP configured on the device
        if cli_response == "":
            return BgpSummary(as_number, bgp_router_identifier, neighbors)

        # Split response into lines
        lines = [
            line.strip() for line in cli_response.splitlines() if line.strip()
        ]

        # Extract AS number and router ID from the second line
        for line in lines:
            if "BGP router identifier" in line:
                match = re.search(
                    r"BGP router identifier (\S+), local AS number (\d+)", line
                )
                if match:
                    bgp_router_identifier = match.group(1)
                    as_number = int(match.group(2))
                break

        # Process each line for neighbor details
        for line in lines:
            if re.match(r"^\d+\.\d+\.\d+\.\d+", line):
                fields = line.split()
                neighbor = fields[0]
                up_down_time = fields[8]
                state_pfx_accepted = BgpSummaryIpv4Decipher.get_state_pfx_accepted(fields[9])

                neighbor_obj = BgpNeighbor(
                    neighbor = neighbor,
                    up_down_time = up_down_time,
                    state_pfx_accepted = state_pfx_accepted,
                )
                neighbors[neighbor] = neighbor_obj

        return BgpSummary(as_number, bgp_router_identifier, neighbors)

    @staticmethod
    def get_state_pfx_accepted(field: str) -> int | str:
        if re.match(r'^([\s\d]+)$', field):
            return int(field)
        return field