import json
import typing
import dataclasses


@dataclasses.dataclass
class IpAddress:
    address: str
    subnet: str = dataclasses.field(init=False)
    cidr_mask: int = dataclasses.field(init=False)

    def __post_init__(self):
        subnet, cidr_mask = self.address.split("/")
        self.cidr_mask = int(cidr_mask)
        self.subnet = subnet

    def encode(self) -> str:
        return self.address


class TopolongyJsonEncoder(json.JSONEncoder):
    def default(selo, o):
        if isinstance(o, IpAddress):
            return o.encode()
        return super().default(o)


TopologyL2L3 = typing.TypedDict(
    "TopologyL2L3",
    {
        "ipv4_subnet": IpAddress,
        "ipv6_subnet": IpAddress,
        "type": str,
        "designed-distance": int,
        "bundle": bool,
        "member-ports": int,
        "member-speed": int,
        "a": str,
        "a_interface": str,
        "z": str,
        "z_interface": str,
        "a_site": str,
        "a_is_device": bool,
        "z_site": str,
        "z_is_device": bool,
        "key": str,
    },
)


Lag = typing.TypedDict(
    "Lag",
    {
        "interface-type": str,
        "interface-id": str,
        "members": list[str],
        "link": str,
        "link-type": str,
        "interface": str,
        "ipv4_address": IpAddress,
        "ipv6_address": IpAddress,
    },
)


Port = typing.TypedDict(
    "Port",
    {
        "interface-type": str,
        "interface-id": str,
        "lag-id": str,
        "link": str,
        "link-type": str,
        "member-speed": int,
        "bundle-member": bool,
        "interface": str,
    },
)


Loopback = typing.TypedDict(
    "Loopback",
    {
        "id": str,
        "description": str,
        "family": str,
        "ip_address": str,
        "algo0_sid": str,
        "algo128_sid": str,
    },
)


Device = typing.TypedDict(
    "Device",
    {
        "loopbacks": list[Loopback],
        "network": str,
        "platform": str,
        "name": str,
        "site": str,
        "role": str,
        "ports": list[Port],
        "lags": list[Lag],
    },
)


Site = typing.TypedDict(
    "Site", {"name": str, "type": list[str], "devices": list[Device]}
)


Network = typing.TypedDict(
    "Network",
    {
        "name": str,
        "planes": int,
        "asn": int,
        "metro-area": str,
        "market-id": int,
        "market-name": str,
        "sites": list[Site],
        "topology-l2l3": list[TopologyL2L3],
    },
)


Inventory = typing.TypedDict(
    "Inventory",
    {"name": str, "type": str, "adjacent-networks": str, "network": Network},
)


def is_instance_of(
    instance: dict[str, typing.Any], t: typing.TypedDict
) -> bool:
    required_keys = set(t.__annotations__.keys())
    instance_keys = set(instance.keys())
    return required_keys == instance_keys


def deserialization_hook(d: dict) -> dict:
    if is_instance_of(d, TopologyL2L3):
        ip_address_keys = ["ipv4_subnet", "ipv6_subnet"]
        for ip_address_key in ip_address_keys:
            d[ip_address_key] = IpAddress(address=d[ip_address_key])
    elif is_instance_of(d, Lag):
        ip_address_keys = ["ipv4_address", "ipv6_address"]
        for ip_address_key in ip_address_keys:
            d[ip_address_key] = IpAddress(address=d[ip_address_key])

    return d
