import json

from automation_utils.helpers.deciphers.drivenets.bgp_summary import (
    BgpSummaryIpv4Decipher as DnosBgpIpv4Decipher,
)
from automation_utils.helpers.deciphers.arista.bgp_summary import (
    BgpSummaryDecipher as AristaBgpDecipher,
)
from automation_utils.data_objects.bgp_summary import BgpSummary, BgpNeighbor


def test_dnos_bgp_summary_ipv4_parser():
    # Arrange
    cli_response = """IPv4 Unicast
---------------------
BGP router identifier 96.109.183.81, local AS number 33287
BGP table node count 5
Table route limit: 2000000
Table route count: 3
Routes over limit: 0

  Neighbor        V         AS MsgRcvd    MsgSent    InQ  OutQ  AdjOut  Up/Down   State/PfxAccepted
  96.109.183.47   4      33287       1403       1424    0     0       0 2d14h25m  190
  96.217.1.14     4 4200001220         39         50    0     0       0 3d12h47m  Connect

Total number of established neighbors with IPv4 Unicast 0/2

Total number of NSR capable BGP sessions 0

Total number of established neighbors 0/2"""

    expected_result = BgpSummary(
        as_number = 33287,
        bgp_router_identifier = "96.109.183.81",
        neighbors = {
            "96.109.183.47": BgpNeighbor(
                neighbor = "96.109.183.47",
                up_down_time = "2d14h25m",
                state_pfx_accepted = 190,
            ),
            "96.217.1.14": BgpNeighbor(
                neighbor = "96.217.1.14",
                up_down_time = "3d12h47m",
                state_pfx_accepted = "Connect",
            )
        }
    )

    # Act
    result = DnosBgpIpv4Decipher.decipher(cli_response)

    # Assert
    assert result == expected_result

def test_arista_bgp_summary_parser():
    # Arrange
    cli_response = json.dumps(
        {
            "vrfs": {
                "default": {
                    "vrf": "default",
                    "routerId": "96.109.183.7",
                    "asn": "33287",
                    "peers": {
                        "2001:558:4c0:0:3000::16": {
                            "description": "IPv6 Unicast to rr02.site2.cran1",
                            "version": 4,
                            "msgReceived": 60272,
                            "msgSent": 2603163,
                            "inMsgQueue": 0,
                            "outMsgQueue": 0,
                            "asn": "33287",
                            "prefixAccepted": 0,
                            "prefixReceived": 0,
                            "upDownTime": "1732583395.43076",
                            "underMaintenance": False,
                            "peerState": "Established",
                        },
                        "2001:558:4c0:660::34": {
                            "description": "IPv6 Unicast to ar01.site51",
                            "version": 4,
                            "msgReceived": 3778255,
                            "msgSent": 3818928,
                            "inMsgQueue": 0,
                            "outMsgQueue": 0,
                            "asn": "4200001220",
                            "prefixAccepted": 217466,
                            "prefixReceived": 217466,
                            "upDownTime": "1732583394.694815",
                            "underMaintenance": False,
                            "peerState": "Established",
                        },
                    },
                }
            }
        }
    )

    expected_result = BgpSummary(
        as_number=33287,
        bgp_router_identifier="96.109.183.7",
        neighbors={
            "2001:558:4c0:0:3000::16": BgpNeighbor(
                neighbor="2001:558:4c0:0:3000::16",
                up_down_time="1732583395.43076",
                state_pfx_accepted=0,
            ),
            "2001:558:4c0:660::34": BgpNeighbor(
                neighbor="2001:558:4c0:660::34",
                up_down_time="1732583394.694815",
                state_pfx_accepted=217466,
            ),
        }
    )

    # Act
    result = AristaBgpDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result