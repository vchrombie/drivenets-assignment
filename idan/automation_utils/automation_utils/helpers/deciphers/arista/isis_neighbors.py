import json

from automation_utils.data_objects.isis_neighbors import (
    IsisNeighbor,
    IsisNeighbors,
)
from automation_utils.helpers.deciphers.decipher_base import Decipher


class IsisNeighborsDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> IsisNeighbors:
        # Parse the JSON string into a Python dictionary
        data = json.loads(cli_response)

        # Initialize neighbors dictionary. Key is the interface name, value is a list of IsisNeighbor.
        neighbors_dict = {}

        # Navigate through the JSON structure to find the instance ID and neighbors
        vrfs = data.get("vrfs", {})
        default_vrf = vrfs.get("default", {})
        isis_instances = default_vrf.get("isisInstances", {})

        # Assuming there's only one instance ID in the JSON
        for instance_id_str, instance_data in isis_instances.items():
            instance_id = int(instance_id_str)
            neighbors = instance_data.get("neighbors", {})

            for neighbor_id, neighbor_data in neighbors.items():
                for adjacency in neighbor_data.get("adjacencies", []):
                    # Create IsisNeighbor object
                    neighbor = IsisNeighbor(
                        system_name=adjacency["hostname"],
                        interface_name=adjacency["interfaceName"],
                        state=adjacency["state"],
                        last_change=str(adjacency["details"]["stateChanged"]),
                    )
                    neighbors_dict.update({adjacency["interfaceName"]: neighbor})

            return IsisNeighbors(instance_id, neighbors_dict)

        raise ValueError("No valid ISIS instance found in the JSON data")
