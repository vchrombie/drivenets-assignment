import re
from automation_utils.data_objects.config_protocols_bgp import ConfigProtocolsBgp
from automation_utils.helpers.deciphers.decipher_base import Decipher


class ShowConfigProtocolsBgpDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> ConfigProtocolsBgp:
        """
        Parse BGP configuration and extract neighbor IP addresses.
        
        Args:
            cli_response (str): CLI response containing BGP configuration
            
        Returns:
            ConfigProtocolsBgp: Object containing parsed BGP configuration data
        """
        neighbors_ip_addresses = []
        
        # Regular expression to match neighbor IP addresses
        # Excludes neighbor-group entries
        neighbor_pattern = r'neighbor\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        
        # Find all neighbor IP addresses
        matches = re.finditer(neighbor_pattern, cli_response)
        for match in matches:
            neighbor_ip = match.group(1)
            neighbors_ip_addresses.append(neighbor_ip)

        return ConfigProtocolsBgp(neighbors_ip_addresses=neighbors_ip_addresses)
