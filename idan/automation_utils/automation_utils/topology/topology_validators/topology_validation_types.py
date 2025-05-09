from enum import Enum

class TopologyValidationType(Enum):
    SYSTEM_STATUS = "system_status"
    INTERFACES_STATUS = "interfaces_status"
    LLDP_NEIGHBORS = "lldp_neighbors"
    PIM_INTERFACES = "pim_interfaces"
    ISIS_NEIGHBORS = "isis_neighbors"
    BGP_NEIGHBORS = "bgp_neighbors"
