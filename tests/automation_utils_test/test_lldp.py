import json
import logging
import pytest

from automation_utils.inventory_manager import InventoryManager
from automation_utils.templates import template_parser
from automation_utils.device_manager import DeviceManager

logger = logging.getLogger()

dnos_settings = {
    "bundle-settings": {
        "AGG_BW": "100G",
        "INTERFACE_MODE": "l3&sub",
        "INTERFACE_TYPE": "bundle",
        "LAG_MIN_LINKS": "1",
        "LAG_NUMBER": "1",
        "REMOTE_HOST": "cdnos",
        "REMOTE_LAG_INTERFACE": "Port-Channel1",
    },
    "bundle-ports": {
        "BUNDLE_MEMBERS": [
            {
                "PORT": "ge400-0/0/0",
                "PORT_BW": "400G",
                "BREAKOUT": "NOBREAKOUT",
                "REMOTE_PORT": "Et1",
                "ADMIN": "up",
                "CHANGE": "",
            }
        ],
        "LAG_NUMBER": "1",
        "LAG_INTERFACE": "bundle-1",
        "PORT_BW": "100G",
        "INTERFACE_MODE": "l3&sub",
        "INTERFACE_TYPE": "AGG-MEMBER",
        "REMOTE_HOST": "ceos",
        "REMOTE_PORT": "Et1",
        "REMOTE_LAG_INTERFACE": "Port-Channel1",
    },
    "bundle-l3-settings": {
        "LAG_NUMBER": "1",
        "INTERFACE_MODE": "l3&sub",
        "IPV4_UNICAST_P2P": "10.1.1.1",
        "IPV6_UNICAST_P2P": "2001:db8:cafe:1:d0f8:9ff6:4201:7086",
        "IPV4_RAN_P2P": "10.1.1.1",
        "IPV6_RAN_P2P": "2001:db8:cafe:1:d0f8:9ff6:4201:7086",
    },
}

arista_settings = {
    "bundle-settings": {
        "BUNDLE_MEMBERS": [
            {
                "PORT": "Et1",
                "PORT_BW": "400G",
                "BREAKOUT": "NOBREAKOUT",
                "REMOTE_PORT": "ge400-0/0/0",
            }
        ],
        "AGG_BW": "100G",
        "INTERFACE_MODE": "l3&sub",
        "INTERFACE_TYPE": "bundle",
        "LAG_MIN_LINKS": 1,
        "LAG_NUMBER": 1,
        "REMOTE_HOST": "cdnos",
        "REMOTE_LAG_INTERFACE": "bundle-1",
    },
    "bundle-ports": {
        "BUNDLE_MEMBERS": [
            {
                "PORT": "Et1",
                "PORT_BW": "400G",
                "BREAKOUT": "NOBREAKOUT",
                "REMOTE_PORT": "ge400-0/0/0",
                "ADMIN": "up",
                "CHANGE": "",
            }
        ],
        "LAG_NUMBER": "1",
        "BW": "400G",
        "INTERFACE_MODE": "l3&sub",
        "INTERFACE_TYPE": "AGG-MEMBER",
        "REMOTE_HOST": "cdnos",
        "REMOTE_PORT": "ge400-0/0/0",
        "REMOTE_LAG_INTERFACE": "bundle-1",
        "INTERFACE_LINK": "bundle",
        "LAG_INTERFACE": "Port-Channel1",
    },
    "bundle-l3-settings": {
        "LAG_NUMBER": "1",
        "INTERFACE_MODE": "l3&sub",
        "IPV4_UNICAST_P2P": "10.1.1.2",
        "IPV6_UNICAST_P2P": "2001:db8:cafe:1:d0f8:9ff6:4201:7087",
        "IPV4_RAN_P2P": "10.1.1.3",
        "LOCAL_ROLE": "pcr",
        "REMOTE_ROLE": "tcr",
        "IPV6_RAN_P2P": "2001:db8:cafe:1:d0f8:9ff6:4201:7089",
    },
}

DNOS_DEVICE = "tcr03"
CEOS_DEVICE = "tcr04"

DEVICE_CONFIG = "tests/automation_utils/resources/config.yml"


@pytest.mark.skip(
    reason="This test communicates with dnos and ceos devices. Update inventory config.yml before execution"
)
class TestLldp:
    def test_lldp(self):
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        # use CLI manager
        m = DeviceManager()
        m.init_devices(inventory_manager.devices)

        print("Applying DNOS configuration....")

        parser = template_parser.TemplateParser(
            platforms=["drivenets-sa-40c"], roles=["tcr"]
        )
        for template_name in dnos_settings:
            rendered = parser.render_template_by_name(
                template_name, dnos_settings[template_name]
            )

            # another option:
            # rendered = template_parser.render_template(
            #                                         template_name=template_name,
            #                                         platforms=["drivenets-sa-40c"],
            #                                         roles=["tcr"],
            #                                         template_vars=dnos_settings[template_name]
            #                                         )

            print(f"\n\n{template_name}:\n{rendered}")

            print("configuring DNOS device....")
            diff = m.cli_sessions[DNOS_DEVICE].edit_config(
                rendered, replace=False, diff=True, stop_on_error=False
            )
            print(f"diff: {diff}")
        print("DNOS configuration has been applied")

        print("Applying ARISTA configuration....")
        parser = template_parser.TemplateParser(
            platforms=["arista-dcs7280dr3a", "arista-dcs7280dr3ak"],
            roles=["pcr"],
        )
        for template_name in arista_settings:
            rendered = parser.render_template_by_name(
                template_name, arista_settings[template_name]
            )

            print(f"\n\n{template_name}:\n{rendered}")
            print("configuring ARISTA device....")
            diff = m.cli_sessions[CEOS_DEVICE].edit_config(
                rendered, replace=False, diff=True, stop_on_error=False
            )
            print(f"diff: {diff}")
        print("Arista configuration has been applied")

        res = m.cli_sessions[CEOS_DEVICE].send_command(
            command="show interfaces|json"
        )
        interfaces_dict = json.loads(res)
        status = interfaces_dict["interfaces"]["Port-Channel1"][
            "interfaceStatus"
        ]
        assert status == "connected"

        lldp_neighbors = m.cli_sessions[CEOS_DEVICE].send_command(
            command="show lldp neighbors|json"
        )
        lldp_dict = json.loads(lldp_neighbors)
        print(lldp_dict)
        # todo assert lldp_dict['lldpNeighbors']
