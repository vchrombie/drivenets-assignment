import json
import time
import logging

import pytest
from automation_utils.inventory_manager import InventoryManager
from automation_utils.cli.cli_ceos import CliCeos
from automation_utils.cli.cli_dnos import CliDnos
from automation_utils.device_manager import DeviceManager
from automation_utils.common.exceptions import (
    UnexpectedOutput,
    CommitFailedException,
)
from automation_utils.helpers.deciphers.drivenets.ping import DnosPingDecipher

logger = logging.getLogger()

CLI_SNIPPET_DNOS = """protocols
  isis
    instance 1
      iso-network 49.0000.0031.0031.0031.0032.00
      interface ge400-0/0/12
        network-type point-to-point
        address-family ipv4-unicast
          metric 10
          !
"""

CLI_WRONG_SNIPPET = """protocols
  bla
"""

CLI_SNIPPET_CEOS = """management ssh
   ip access-group IPV4-VTY-ACCESS-IN-ACL in
   ipv6 access-group IPV6-VTY-ACCESS-IN-ACL in
   idle-timeout 10
   authentication mode password
   connection limit 16
   login timeout 30
!
"""

CLI_BANNER = """      ********************************************************************************

      ================     WARNING THIS DEVICE IS MANAGED BY PNP     =================
      ================ MANUAL CHANGES MIGHT RESULT IN SERVICE IMPACT =================
      ================ ALL CONFIG CHANGES MUST BE MADE VIA NETADMIN  =================

      ********************************************************************************"""

DNOS_BANNER_SNIPPET = """system
        login
          banner "{banner}"
        !
      !
"""

CEOS_BANNER_SNIPPET = """banner login
      {banner}
      EOF"""

DEVICE_CONFIG = "tests/automation_utils/resources/config.yml"


@pytest.mark.skip(
    reason="This test communicates with dnos and ceos devices. Update inventory config.yml before execution"
)
class TestCli:
    def test_cli_without_manager(self):
        # create the inventory object from yaml file
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)

        # use CLI object directly, without manager
        dut = inventory_manager.devices["tcr03"]
        cli = CliDnos(dut.hostname, dut.username, dut.password)

        # the session is not opened after the initialization
        assert not cli.is_connected()

        # send_command will open the session if not opened
        res = cli.send_command(command="show system version")
        print(f"show system version: {res}")
        assert "Version: DNOS" in res
        assert cli.is_connected()
        cli.close_session()

    @staticmethod
    def _get_dnos_cli():
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        dut = inventory_manager.devices["tcr03"]
        return CliDnos(dut.hostname, dut.username, dut.password)

    def test_cli_with_manager(self):
        # create the inventory object from yaml file
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        # use Device manager
        m = DeviceManager()
        m.init_devices(inventory_manager.devices)
        cli = m.cli_sessions["tcr03"]

        # not mandatory. can be used for scenarios where
        # sending commands is not necessary
        print("opening session....")
        cli.open_session()
        assert cli.is_connected()

        print("executing rollback 1....")
        cli.rollback(1)

        try:
            print("executing config commands....")
            diff = cli.edit_config(CLI_SNIPPET_DNOS, replace=False, diff=True)
            print(f"diff: {diff}")
        except CommitFailedException as ex:
            if "no configuration changes were made" in str(ex):
                print("Empty commit")
            else:
                raise

        print("executing config command that should fail...")
        with pytest.raises(UnexpectedOutput):
            cli.edit_config(CLI_WRONG_SNIPPET)

        print("executing interactive command...")
        cli.execute_request_command(
            command="request system process restart ncc 0 routing-engine techsupport_manager"
        )
        cli.close_session()

    def test_commit_confirm(self):
        cli = self._get_dnos_cli()
        print("executing config with commit confirm ....")
        cli.edit_config(
            "interface bundle-1 description test", confirm_timeout=1
        )

        print("executing config with commit confirm ....")
        cli.confirm_commit()
        cli.close_session()

    def test_ping(self):
        cli = self._get_dnos_cli()
        res = cli.send_command(
            command="run ping 1.1.1.1", decipher=DnosPingDecipher
        )
        print(res)
        cli.close_session()

    def test_arista(self):
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        dut = inventory_manager.devices["tcr04"]
        ceos_cli = CliCeos(dut.hostname, dut.username, dut.password)
        ceos_cli.open_session()
        assert ceos_cli.is_connected()
        res = ceos_cli.send_command(command="show version")
        print(f"show version: {res}")
        assert "Arista" in res

        print("executing ping command....")
        res = ceos_cli.send_command(command="ping 1.1.1.1")
        print(res)

        print("executing config commands....")
        session_name = "auto_test_%d" % (time.time() * 100)
        diff = ceos_cli.edit_config(
            CLI_SNIPPET_CEOS,
            replace=False,
            diff=True,
            session_name=session_name,
        )
        print(f"diff: {diff}")

        print("Verifying that the configuration session is closed...")
        res = ceos_cli.send_command(command="show configuration sessions")
        assert session_name not in res

        print("executing config command that should fail...")
        session_name = "auto_test_%d" % (time.time() * 100)
        print(f"session_name={session_name}")
        with pytest.raises(UnexpectedOutput):
            ceos_cli.edit_config(CLI_WRONG_SNIPPET, session_name=session_name)
        ceos_cli.close_session()

    def test_banner(self):
        dnos_banner_config = DNOS_BANNER_SNIPPET.format(
            banner=CLI_BANNER.replace("\n", "\\n")
        )
        ceos_banner_config = CEOS_BANNER_SNIPPET.format(banner=CLI_BANNER)
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        m = DeviceManager()
        m.init_devices(inventory_manager.devices)
        dnos_cli = m.cli_sessions["tcr03"]
        ceos_cli = m.cli_sessions["tcr04"]
        print("configuring DNOS banner....")
        diff = dnos_cli.edit_config(
            dnos_banner_config, replace=False, diff=True
        )
        print(f"diff: {diff}")
        print("configuring CEOS banner....")
        diff = ceos_cli.edit_config(
            ceos_banner_config, replace=False, diff=True
        )
        print(f"diff: {diff}")

    def test_arista_show_parsers(self):
        inventory_manager = InventoryManager()
        inventory_manager.load(DEVICE_CONFIG)
        dut = inventory_manager.devices["tcr04"]
        ceos_cli = CliCeos(dut.hostname, dut.username, dut.password)
        ceos_cli.open_session()

        # parse with NTC Templates
        # pip install ntc-templates
        from ntc_templates.parse import parse_output

        res = ceos_cli.send_command(command="show interfaces")
        interfaces_parsed = parse_output(
            platform="arista_eos", command="show interfaces", data=res
        )
        link_status = interfaces_parsed[0]["link_status"]

        # use vendors JSON
        res = ceos_cli.send_command(command="show interfaces|json")
        interfaces_dict = json.loads(res)
        status = interfaces_dict["interfaces"]["Ethernet2"]["interfaceStatus"]

        res = ceos_cli.send_command(command="show bgp neighbors|json")
        bgp_neighbors_dict = json.loads(res)
        peer_address = bgp_neighbors_dict["vrfs"]["default"]["peerList"][0][
            "peerAddress"
        ]
        # peer_address: '2.2.2.2'
        peer_state = bgp_neighbors_dict["vrfs"]["default"]["peerList"][0][
            "state"
        ]
        # peer_state: 'Established'
