class ConfigProtocolsBgp:
    def __init__(self, neighbors_ip_addresses: list[str]):
        self.neighbors_ip_addresses = neighbors_ip_addresses

    def __eq__(self, other):
        if not isinstance(other, ConfigProtocolsBgp):
            return False
        return self.neighbors_ip_addresses == other.neighbors_ip_addresses

    def __repr__(self):
        return f"ConfigProtocolsBgp(neighbors_ip_addresses={self.neighbors_ip_addresses})"
