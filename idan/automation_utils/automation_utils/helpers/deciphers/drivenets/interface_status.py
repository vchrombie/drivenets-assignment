from automation_utils.helpers.deciphers.decipher_base import Decipher
from automation_utils.data_objects.interface_status import InterfaceStatus


class InterfacesStatusDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> dict[str, InterfaceStatus]:
        interfaces = {}
        
        # Split the response into lines
        lines = cli_response.strip().split('\n')
        
        # Skip the header and separator lines
        data_lines = lines[2:]
        
        for line in data_lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Split the line by '|' and remove whitespace
            fields = [field.strip() for field in line.split('|')]
            
            # Remove empty strings from the beginning and end of the list
            fields = [f for f in fields if f]
            
            # Create InterfaceStatus object
            if len(fields) >= 3:  # Ensure we have at least the required fields
                interface = InterfaceStatus(
                    interface=fields[0],
                    admin_status=fields[1],
                    operational_status=fields[2]
                )
                interfaces[fields[0]] = interface
                
        return interfaces