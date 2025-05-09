from typing import List


class NextHop:
    def __init__(self, ip_address: str, interface: str=None, is_active: bool=False, is_recursive: bool=False, is_alternate: bool=False):
        self.ip_address = ip_address
        self.interface = interface
        self.is_active = is_active
        self.is_recursive = is_recursive
        self.is_alternate = is_alternate

    def __eq__(self, other):
        if not isinstance(other, NextHop):
            return False
        return (
            self.ip_address == other.ip_address
            and self.interface == other.interface 
            and self.is_active == other.is_active
            and self.is_recursive == other.is_recursive
            and self.is_alternate == other.is_alternate
        )
    
    def __repr__(self):
        return f"NextHop(ip_address='{self.ip_address}', interface='{self.interface}', is_active='{self.is_active}', is_recursive='{self.is_recursive}', is_alternate='{self.is_alternate}')"


class IpRoute:
    def __init__(
        self, destination: str, protocol: str, next_hops: List[NextHop]
    ):
        self.destination = destination
        self.protocol = protocol
        self.next_hops = next_hops

    def __eq__(self, other):
        if not isinstance(other, IpRoute):
            return False
        return (
            self.destination == other.destination
            and self.protocol == other.protocol
            and self.next_hops == other.next_hops
        )

    def __repr__(self):
        return (
            f"IpRoute(destination='{self.destination}', "
            f"protocol='{self.protocol}', "
            f"next_hops={self.next_hops})"
        )
