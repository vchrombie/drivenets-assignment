from automation_utils.data_objects.system_status import SystemStatus
from automation_utils.helpers.deciphers.decipher_base import Decipher


class SystemStatusDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> SystemStatus:
        # Initialize dictionary to hold status information
        status_dict = {}

        # Split response into lines
        lines = [
            line.strip() for line in cli_response.splitlines() if line.strip()
        ]

        # Find the start of the table
        table_start = False
        for line in lines:
            if line.startswith("| Type |"):
                table_start = True
                continue

            if table_start and line.startswith("|"):
                # Split the line by '|' and strip whitespace
                fields = [field.strip() for field in line.split("|")]

                # Map 'Type' to 'Operational'
                if len(fields) > 4:
                    type_key = fields[1]
                    operational_value = fields[4]
                    status_dict[type_key] = operational_value

        return SystemStatus(status_dict)
