from automation_utils.helpers.deciphers.drivenets.interface_status import InterfacesStatusDecipher
from automation_utils.data_objects.interface_status import InterfaceStatus


def test_interfaces_status_decipher():
    # Test input
    cli_response = """| Interface                |  Admin   | Operational     | IPv4 Address           | IPv6 Address                                | VLAN          | MTU  | Network-Service                             | Bundle-Id  |
+--------------------------+----------+-----------------+------------------------+---------------------------------------------+---------------+------+---------------------------------------------+------------+
| bundle-340               | enabled  | up              | 96.217.1.190/30        | 2001:558:4c0:511::190/64                    |               | 9192 | VRF (default)                               |            |
| bundle-721               | enabled  | up              | 96.217.3.182/30        | 2001:558:4c0:634::182/64                    |               | 9192 | VRF (default)                               |            |
| ge400-0/0/0              | disabled | not-present     |                        |                                             |               | 1514 | VRF (default)                               |            |"""

    # Decipher the CLI response
    result = InterfacesStatusDecipher.decipher(cli_response)

    # Expected results as a dictionary
    expected_results = {
        "bundle-340": InterfaceStatus(interface="bundle-340", admin_status="enabled", operational_status="up"),
        "bundle-721": InterfaceStatus(interface="bundle-721", admin_status="enabled", operational_status="up"),
        "ge400-0/0/0": InterfaceStatus(interface="ge400-0/0/0", admin_status="disabled", operational_status="not-present")
    }

    # Verify the results
    assert len(result) == len(expected_results)
    for interface, expected in expected_results.items():
        assert interface in result
        assert result[interface] == expected