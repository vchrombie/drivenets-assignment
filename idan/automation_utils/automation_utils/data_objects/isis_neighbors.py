class IsisNeighbor:
    def __init__(
        self,
        system_name: str,
        interface_name: str,
        state: str,
        last_change: str,
    ):
        self.system_name = system_name
        self.interface_name = interface_name
        self.state = state
        self.last_change = last_change

    def __eq__(self, other):
        if not isinstance(other, IsisNeighbor):
            return False
        return (
            self.system_name == other.system_name
            and self.interface_name == other.interface_name
            and self.state == other.state
            and self.last_change == other.last_change
        )

    def __repr__(self):
        return (
            f"IsisNeighbor(system_name='{self.system_name}', "
            f"interface_name='{self.interface_name}', "
            f"state='{self.state}', "
            f"last_change='{self.last_change}')"
        )


class IsisNeighbors:
    def __init__(self, instance_id: int, neighbors: dict[str, list[IsisNeighbor]]):
        self.instance_id = instance_id
        self.neighbors = neighbors

    def __eq__(self, other):
        if not isinstance(other, IsisNeighbors):
            return False
        return (
            self.instance_id == other.instance_id
            and self.neighbors == other.neighbors
        )

    def __repr__(self):
        return (
            f"IsisNeighbors(instance_id={self.instance_id}, "
            f"neighbors={self.neighbors})"
        )
