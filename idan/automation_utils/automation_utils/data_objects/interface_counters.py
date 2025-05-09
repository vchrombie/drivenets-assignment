class InterfaceCounters:
    def __init__(self, interface_name: str, rx_mbps: float, tx_mbps: float):
        self.interface_name = interface_name
        self.rx_mbps = rx_mbps
        self.tx_mbps = tx_mbps

    def __eq__(self, other):
        if not isinstance(other, InterfaceCounters):
            return False
        return (
            self.interface_name == other.interface_name
            and self.rx_mbps == other.rx_mbps
            and self.tx_mbps == other.tx_mbps
        )

    def __repr__(self):
        return (
            f"InterfaceCounters(interface_name={self.interface_name}, "
            f"rx_mbps={self.rx_mbps}, "
            f"tx_mbps={self.tx_mbps})"
        )
