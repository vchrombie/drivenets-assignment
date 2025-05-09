from automation_utils.data_objects.ip_route import IpRoute, NextHop
from typing import Optional


class IpRouteDecipher:
    @staticmethod
    def decipher(route_text: str) -> Optional[IpRoute]:
        lines = route_text.splitlines()
        destination = None
        protocol = None
        next_hops = []

        is_alternate = False
        for line in lines:
            line = line.strip()
            
            # Extract destination
            if "Routing entry for" in line:
                destination = line.split("Routing entry for")[1].strip()
            
            # Extract protocol
            elif "Known via" in line:
                protocol = line.split('"')[1].strip()
            
            # Parse next hops
            elif any(char.isdigit() for char in line):
                # Skip lines that don't contain IP addresses
                if "Last update" in line:
                    continue
                if not any(segment.count('.') == 3 or ':' in segment for segment in line.split()):
                    continue
                
                is_active = line.startswith('*')
                is_recursive = False
                if '(recursive)' in line:
                    is_recursive = True
                    if 'alternate' not in line:
                        # reset is_alternate to False for the next hops
                        is_alternate = False
                if 'alternate' in line:
                    # mark all the next hops as alternate
                    is_alternate = True
                
                
                # Clean up the line by removing markers
                clean_line = line.replace('*', '').replace('(recursive)', '').replace('alternate', '').strip()
                
                # Extract IP and interface
                parts = clean_line.split(',', 1)
                if len(parts) == 1:
                    next_hop = NextHop(ip_address=parts[0].strip(), is_recursive=is_recursive, is_alternate=is_alternate)
                    next_hops.append(next_hop)
                    continue
                    
                ip_address = parts[0].strip()
                interface = parts[1].replace('via', '').strip().split()[0]
                
                next_hop = NextHop(
                    ip_address=ip_address,
                    interface=interface,
                    is_active=is_active,
                    is_alternate=is_alternate,
                    is_recursive=is_recursive
                )
                next_hops.append(next_hop)

        if destination and protocol:
            return IpRoute(destination=destination, protocol=protocol, next_hops=next_hops)
        return None
