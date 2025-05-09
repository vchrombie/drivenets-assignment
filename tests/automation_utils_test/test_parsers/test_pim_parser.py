from automation_utils.helpers.deciphers.drivenets.pim_protocol import PimConfigDecipher, PimNeighborsDecipher
from automation_utils.data_objects.pim_data import PimData


def test_pim_config_decipher():
    # Arrange
    cli_response = """protocols
  pim
    graceful-restart-timer 90
    hello-interval 1
    ssm-ranges SSM-RANGE-PFX
    address-family ipv4
      interface bundle-340
        admin-state enabled
      !
      interface bundle-721
        admin-state enabled
      !
    !
  !
!"""

    expected_result = [
        "bundle-340",
        "bundle-721"
    ]

    # Act
    result = PimConfigDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result

def test_pim_operational_decipher():
    cli_response = """| Neighbor Address | Interface | Uptime | Expires |
+------------------------+-----------+-------+---------+
| 2001:558:4c0:634::182  | bundle-721| 00:00:00| 00:00:00|
| 2001:558:4c0:511::190  | bundle-340| 00:00:00| 00:00:00|"""

    expected_result = {
        "bundle-721": PimData(neighbor="2001:558:4c0:634::182", interface="bundle-721", uptime="00:00:00"),
        "bundle-340": PimData(neighbor="2001:558:4c0:511::190", interface="bundle-340", uptime="00:00:00")
    }

    result = PimNeighborsDecipher.decipher(cli_response)

    assert result == expected_result
