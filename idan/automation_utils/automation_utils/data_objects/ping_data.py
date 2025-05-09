from dataclasses import dataclass


@dataclass
class PingResponse:
    source: str
    time: float
    sent: int
    received: int
    min_time: float
    avg_time: float
    max_time: float
    std_dev: float
    bytes: int
    sequence: int
    ttl: int


@dataclass
class Status:
    name: str
    value: int


@dataclass
class PingData:
    def __init__(self):
        self.responses = {}
        self.status = None
        self.result_message = None

    responses: dict[int, PingResponse]
    status: Status
    result_message: str
