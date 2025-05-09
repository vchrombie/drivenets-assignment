import re

from automation_utils.data_objects.isis_neighbors import (
    IsisNeighbor,
    IsisNeighbors,
)
from automation_utils.helpers.deciphers.decipher_base import Decipher


class IsisConfigDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> set[str]:
        bundle_ids = set()
        for line in cli_response.splitlines():
            if "interface bundle-" in line:
                bundle_id = line.split()[1] 
                bundle_ids.add(bundle_id)
        return bundle_ids


class IsisNeighborsDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> IsisNeighbors:
        # Initialize neighbors dictionary. Key is the interface name, value is a IsisNeighbor.
        neighbors_dict = {}

        # Split response into lines
        lines = [
            line.strip() for line in cli_response.splitlines() if line.strip()
        ]

        # Extract instance ID from first line
        instance_match = re.match(r"Instance (\d+):", lines[0])
        if not instance_match:
            raise ValueError("Could not find ISIS instance ID in the output")
        instance_id = int(instance_match.group(1))

        # Skip header lines (first 2 lines)
        data_lines = lines[2:]

        # Process each line
        for line in data_lines:
            # Split fields and remove empty strings
            fields = [
                field.strip() for field in line.split("  ") if field.strip()
            ]

            # Create IsisNeighbor object
            neighbor = IsisNeighbor(
                system_name=fields[0],
                interface_name=fields[1],
                state=fields[3],
                last_change=fields[4],
            )
            neighbors_dict.update({fields[1]: neighbor})

        return IsisNeighbors(instance_id, neighbors_dict)
