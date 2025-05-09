from dataclasses import dataclass

@dataclass
class InterfaceStatus:
    interface: str
    admin_status: str
    operational_status: str