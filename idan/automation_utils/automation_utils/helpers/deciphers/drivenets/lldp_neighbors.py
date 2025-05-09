from automation_utils.data_objects.lldp_neighbors import LldpNeighbor
from automation_utils.helpers.deciphers.decipher_base import Decipher


class LldpNeighborsDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> dict:
        # Initialize result dictionary
        neighbors_dict = {}

        # Split response into lines and remove empty lines
        lines = [
            line.strip() for line in cli_response.splitlines() if line.strip()
        ]

        # Skip header lines (first 2 lines including the separator)
        data_lines = lines[2:]

        # Process each line
        for line in data_lines:
            # Split by '|' and strip whitespace from each field
            fields = [field.strip() for field in line.split("|")]

            # Skip empty or invalid lines
            if (
                len(fields) != 6
            ):  # 6 because split('|') on '|x|' gives ['', 'x', '']
                continue

            # Extract fields (ignore first and last empty strings from split)
            interface, system_name, neighbor_interface, ttl = fields[1:5]
            
            # Skip entries with missing neighbor information
            if not all([system_name, neighbor_interface, ttl]):
                continue

            # Create LldpNeighbor object and add to dictionary
            try:
                neighbor = LldpNeighbor(
                    interface, system_name, neighbor_interface, int(ttl)
                )
                neighbors_dict[interface] = neighbor  # Use interface as key
            except ValueError:
                # Skip entries with invalid TTL values
                continue

        return neighbors_dict
