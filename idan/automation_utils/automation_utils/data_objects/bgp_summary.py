
class BgpNeighbor:
    def __init__(self, neighbor: str, up_down_time: str, state_pfx_accepted: int | str):
        self.neighbor = neighbor
        self.up_down_time = up_down_time
        self.state_pfx_accepted: int | str = state_pfx_accepted

    def __eq__(self, other):
        if not isinstance(other, BgpNeighbor):
            return False
        return (
            self.neighbor == other.neighbor
            and self.up_down_time == other.up_down_time
            and self.state_pfx_accepted == other.state_pfx_accepted
        )

    def __repr__(self):
        return (
            f"BgpNeighbor(neighbor='{self.neighbor}', "
            f"up_down_time='{self.up_down_time}', "
            f"state_pfx_accepted={self.state_pfx_accepted})"
        )


class BgpSummary:
    def __init__(
        self, as_number: int | None, bgp_router_identifier: str | None, neighbors: dict[str: BgpNeighbor]
    ):
        self.as_number = as_number
        self.bgp_router_identifier = bgp_router_identifier
        self.neighbors = neighbors

    def __eq__(self, other):
        if not isinstance(other, BgpSummary):
            return False
        return (
            self.as_number == other.as_number
            and self.bgp_router_identifier == other.bgp_router_identifier
            and self.neighbors == other.neighbors
        )

    def __repr__(self):
        return (
            f"BgpSummary(as_number={self.as_number}, "
            f"bgp_router_identifier='{self.bgp_router_identifier}', "
            f"neighbors={self.neighbors})"
        )
