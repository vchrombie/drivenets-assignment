import json

from automation_utils.data_objects.lldp_neighbors import LldpNeighbor
from automation_utils.helpers.deciphers.decipher_base import Decipher


class LldpNeighborsDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> dict:
        # Parse the JSON string into a Python dictionary
        data = json.loads(cli_response)

        # Initialize result dictionary
        neighbors_dict = {}

        # Iterate over each neighbor entry
        for neighbor in data.get("lldpNeighbors", []):
            # Create LldpNeighbor object using the mapped fields
            neighbor_obj = LldpNeighbor(
                interface=neighbor["port"],
                system_name=neighbor["neighborDevice"],
                neighbor_interface=neighbor["neighborPort"],
                ttl=neighbor["ttl"],
            )
            neighbors_dict[neighbor["port"]] = neighbor_obj

        return neighbors_dict
