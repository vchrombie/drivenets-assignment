class SystemStatus:
    def __init__(self, status_dict: dict[str, str]):
        self.status = status_dict

    def __eq__(self, other):
        if not isinstance(other, SystemStatus):
            return False
        return self.status == other.status

    def __repr__(self):
        return f"SystemStatus(status={self.status})"
