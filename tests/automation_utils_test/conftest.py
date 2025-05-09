import pytest
from automation_utils.inventory_manager import InventoryManager
from automation_utils.device_manager import DeviceManager
from automation_utils.topology.topology_manager import TopologyManager


DEVICE_CONFIG = "device_config"
TOPOLOGY_CONFIG = "topology_config"


@pytest.fixture(scope="class")
def device_config(request):
    return request.param


@pytest.fixture(scope="class")
def inventory_manager(device_config):
    # create the inventory object from yaml file
    _inventory = InventoryManager()
    _inventory.load(device_config)
    return _inventory


@pytest.fixture()
def device_manager(inventory_manager, scope="class"):
    m = DeviceManager()
    m.init_devices(inventory_manager.devices)
    return m

@pytest.fixture(scope="class")
def topology_config(request):
    return request.param

@pytest.fixture(scope="class")
def topology_manager(topology_config):
    manager = TopologyManager()
    manager.load(topology_config)
    return manager
