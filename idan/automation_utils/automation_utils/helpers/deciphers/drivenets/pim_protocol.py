from automation_utils.helpers.deciphers.decipher_base import Decipher
from automation_utils.data_objects.pim_data import PimData

class PimConfigDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> list[str]:
        """
        Decipher PIM configuration and extract interface names.
        
        Args:
            cli_response: CLI output containing PIM configuration
            
        Returns:
            List of interface names found in PIM configuration
        """
        interfaces = []
        lines = cli_response.splitlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('interface '):
                # Extract interface name between 'interface ' and newline/whitespace
                interface_name = line.split()[1]
                interfaces.append(interface_name)
                
        return interfaces

class PimNeighborsDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> dict[str, PimData]:
        """
        Decipher PIM operational data and extract neighbor information.
        
        Args:
            cli_response: CLI output containing PIM neighbor table
            
        Returns:
            Dictionary of PimData objects containing neighbor information.
            The key is the interface name.
        """
        pim_neighbors = {}
        lines = cli_response.splitlines()
        
        # Skip header and footer lines
        data_lines = [line.strip() for line in lines if line.startswith('|') and line.strip()]
        
        for line in data_lines[1:]:
            if not line:
                continue
                
            # Split on | and strip whitespace
            fields = [f.strip() for f in line.split('|')[1:-1]]
            
            if len(fields) == 4:
                neighbor_addr, interface, uptime, expires = fields
                pim_neighbors[interface] = PimData(
                    neighbor=neighbor_addr,
                    interface=interface, 
                    uptime=uptime
                )
                
        return pim_neighbors