import json

from automation_utils.data_objects.bgp_summary import BgpSummary, BgpNeighbor
from automation_utils.helpers.deciphers.decipher_base import Decipher


class BgpSummaryDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> BgpSummary:
        # Parse the JSON string into a Python dictionary
        data = json.loads(cli_response)

        # Get the default VRF data
        default_vrf = data.get("vrfs", {}).get("default", {})

        # Extract basic BGP information
        as_number = int(default_vrf.get("asn", 0))
        bgp_router_identifier = default_vrf.get("routerId", "")

        # Process peers
        neighbors: dict[str: BgpNeighbor] = {}
        for neighbor_ip, peer_data in default_vrf.get("peers", {}).items():
            up_down_time = peer_data.get("upDownTime", 0)

            neighbor = BgpNeighbor(
                neighbor=neighbor_ip,
                up_down_time=up_down_time,
                state_pfx_accepted=int(peer_data.get("prefixAccepted", 0)),
            )
            neighbors[neighbor_ip] = neighbor

        return BgpSummary(as_number, bgp_router_identifier, neighbors)
