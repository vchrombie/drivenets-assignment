from abc import ABC, abstractmethod
from automation_utils.topology.topology_manager import TopologyManager
from automation_utils.device_manager import DeviceManager
from automation_utils.topology.topology_validators.topology_validation_types import TopologyValidationType
from automation_utils.common.vendors import Vendors


# IMPORTANT: add the new validators imports to the topology_validators/__init__.py to auto-register them

class TopologyValidatorBase(ABC):
    """
    Abstract base class for topology validators.
    """
    def __init__(self):
        self.topology_manager: TopologyManager = TopologyManager()
        self.device_manager: DeviceManager = DeviceManager()

    @abstractmethod
    def validate(self, device: str, **kwargs):
        """
        Validate the topology components. Can return test artifacts for the later use by the test framework.
        """
        return None


class TopologyValidatorRegistry():
    """
    Topology validator factory. 
    Registers validators and returns them, according to the validation type and vendor.
    """
    _validators = {}

    @staticmethod
    def register_validator(validation_type: TopologyValidationType, vendor: Vendors):
        def decorator(cls):
            TopologyValidatorRegistry._validators[(validation_type.value, vendor.value)] = cls
            return cls
        return decorator

    @staticmethod
    def get_validator(validation_type: TopologyValidationType, vendor: Vendors):
        validator_class = TopologyValidatorRegistry._validators.get((validation_type.value, vendor))
        if validator_class is None:
            raise ValueError("Unsupported validation type or vendor")
        return validator_class()  # Instantiate the validator class
