import json
from automation_utils.helpers.deciphers.arista.interface_counters import (
    InterfaceCountersDecipher as AristaInterfaceCountersDecipher,
)
from automation_utils.helpers.deciphers.drivenets.interface_counters import (
    InterfaceCountersDecipher as DnosInterfaceCountersDecipher,
)
from automation_utils.data_objects.interface_counters import InterfaceCounters


def test_dnos_interface_counters_parser():
    # Arrange
    cli_response = """| Interface          | Operational   | RX[Mbps]            | TX[Mbps]            | RX[pkts]            | TX[pkts]            | RX drops[pkts]      | TX drops[pkts]      |
+--------------------+---------------+---------------------+---------------------+---------------------+---------------------+---------------------+---------------------+
| bundle-178         | up            | 0.06                | 0.05                | 1966761312          | 4090524128          | 0                   | 0                   |
| bundle-247         | up            | 1006.64             | 0.03                | 214047042           | 656255              | 0                   | 0                   |
| bundle-349         | up            | 0.08                | 1006.71             | 3471839914          | 3672616471          | 5                   | 0                   |"""

    expected_result = {
        "bundle-178": InterfaceCounters("bundle-178", 0.06, 0.05),
        "bundle-247": InterfaceCounters("bundle-247", 1006.64, 0.03),
        "bundle-349": InterfaceCounters("bundle-349", 0.08, 1006.71),
    }

    # Act
    result = DnosInterfaceCountersDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result


def test_arista_interface_counters_parser():
    # Arrange
    cli_response = json.dumps(
        {
            "interfaces": {
                "Ethernet1/1": {
                    "description": "PHY|100G|AGG-MEMBER|CORE|type:JANUS-P2P|rhost:ar01.site51.cran1|rport:HundredGigE0/0/0/10|lagg:po277|ragg:be277",
                    "interval": 30,
                    "inBpsRate": 314.0354530371204,
                    "inPktsRate": 3.7114548290247295e-07,
                    "inPpsRate": 0.35693768665845294,
                    "outBpsRate": 429.531528367689,
                    "outPktsRate": 5.311710789735807e-07,
                    "outPpsRate": 0.635247191286823,
                    "lastUpdateTimestamp": 1733168898.2399433,
                },
                "Ethernet2/1": {
                    "description": "PHY|100G|AGG-MEMBER|CORE|type:JANUS-P2P|rhost:ar01.site51.cran1|rport:HundredGigE0/0/0/11|lagg:po277|ragg:be277",
                    "interval": 30,
                    "inBpsRate": 3051.6680766176987,
                    "inPktsRate": 3.262156530602036e-06,
                    "inPpsRate": 1.3155528374021048,
                    "outBpsRate": 150.83127033454355,
                    "outPktsRate": 1.7037862827480273e-07,
                    "outPpsRate": 0.12217098712661975,
                    "lastUpdateTimestamp": 1733168898.2399428,
                },
                "Ethernet3/1": {
                    "description": "",
                    "interval": 300,
                    "inBpsRate": 0.0,
                    "inPktsRate": 0.0,
                    "inPpsRate": 0.0,
                    "outBpsRate": 0.0,
                    "outPktsRate": 0.0,
                    "outPpsRate": 0.0,
                    "lastUpdateTimestamp": 1733168898.2399428,
                },
            }
        }
    )

    # Calculate expected Mbps values (Bps * 8 / 1_000_000)
    expected_result = {
        "Ethernet1/1": InterfaceCounters(
            "Ethernet1/1",
            rx_mbps=314.0354530371204 * 8 / 1_000_000,
            tx_mbps=429.531528367689 * 8 / 1_000_000,
        ),
        "Ethernet2/1": InterfaceCounters(
            "Ethernet2/1",
            rx_mbps=3051.6680766176987 * 8 / 1_000_000,
            tx_mbps=150.83127033454355 * 8 / 1_000_000,
        ),
        "Ethernet3/1": InterfaceCounters("Ethernet3/1", rx_mbps=0.0, tx_mbps=0.0),
    }

    # Act
    result = AristaInterfaceCountersDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result
