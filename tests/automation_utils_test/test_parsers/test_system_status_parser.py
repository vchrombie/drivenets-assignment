from automation_utils.helpers.deciphers.drivenets.system_status import (
    SystemStatusDecipher,
)
from automation_utils.data_objects.system_status import SystemStatus


def test_system_status_parser():
    # Arrange
    cli_response = """
System Name: pcr01.site10.cran1, System-Id: 52c52573-0ef7-4778-9779-8870bcebdbaf
System Type: SA-36CD-S, Family: NCR
Enterprise-Id: 49739
Description: DRIVENETS Network Cloud Router
System status: running 
System Start Time: 09-Nov-2024 16:27:45 UTC
System Uptime: 17 days, 4:19:38
System Boot Uptime: 17 days, 4:20:33
Version: DNOS [19.2.0] build [10], Copyright 2024 DRIVENETS LTD.
Patch: N/A
Environment:
        Location: Janustest10
        Floor: N/A
        Rack: N/A
Contact: support@drivenets.com
Fabric Minimum Links: N/A
Fabric Minimum NCF: N/A
NCC switchovers: 0
Last NCC switchover: N/A
Escalation-stop-failovers
  Max-failover(remaining): 2(2)
  Failover-period(remaining): 30min(0 days, 0:30:00)
Recovery-mode: supported
BGP NSR: N/A


| Type | Id     | Admin    | Operational                        | Model          | Uptime              | Description                | Serial Number        |
+------+--------+----------+------------------------------------+----------------+---------------------+----------------------------+----------------------+
| NCC  | 0      |          | active-up                          | NCP-36CD-S     | 17 days, 4:19:38    | dn-ncc-0                   |                      |
| NCP  | 0      | enabled  | up                                 | NCP-36CD-S     | 17 days, 4:17:13    | dn-ncp-0                   | WKY1C8VS0001BP2      |
"""

    expected_result = SystemStatus({"NCC": "active-up", "NCP": "up"})

    # Act
    result = SystemStatusDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result
