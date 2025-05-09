class PimData:
    def __init__(self, neighbor: str, interface: str, uptime: str):
        self.neighbor = neighbor
        self.interface = interface
        self.uptime = uptime

    def __eq__(self, other):
        return self.neighbor == other.neighbor and self.interface == other.interface and self.uptime == other.uptime
