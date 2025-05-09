from automation_utils.data_objects.interface_counters import InterfaceCounters
from automation_utils.helpers.deciphers.decipher_base import Decipher


class InterfaceCountersDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> dict:
        # Initialize result dictionary
        counters_dict = {}

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
                len(fields) < 9
            ):  # We expect at least 9 fields including empty ones at start/end
                continue

            # Extract relevant fields
            interface_name = fields[1]
            rx_mbps = float(fields[3])
            tx_mbps = float(fields[4])

            # Create InterfaceCounters object and add to list
            counter = InterfaceCounters(
                interface_name=interface_name, rx_mbps=rx_mbps, tx_mbps=tx_mbps
            )
            counters_dict[interface_name] = counter

        return counters_dict
