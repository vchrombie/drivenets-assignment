class LldpNeighbor:
    def __init__(self, interface, system_name, neighbor_interface, ttl):
        self.interface = interface
        self.system_name = system_name
        self.neighbor_interface = neighbor_interface
        self.ttl = ttl

    def __eq__(self, other):
        if not isinstance(other, LldpNeighbor):
            return False
        return (
            self.interface == other.interface
            and self.system_name == other.system_name
            and self.neighbor_interface == other.neighbor_interface
        )

    def __repr__(self):
        return (
            f"LldpNeighbor(interface={self.interface}, "
            f"system_name={self.system_name}, "
            f"neighbor_interface={self.neighbor_interface}"
        )
