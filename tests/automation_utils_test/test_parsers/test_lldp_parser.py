import json
from automation_utils.helpers.deciphers.arista.lldp_neighbors import (
    LldpNeighborsDecipher as AristaLldpDecipher,
)
from automation_utils.helpers.deciphers.drivenets.lldp_neighbors import (
    LldpNeighborsDecipher as DnosLldpDecipher,
)
from automation_utils.data_objects.lldp_neighbors import LldpNeighbor


def test_dnos_lldp_neighbors_parser():
    # Arrange
    cli_response = """| Interface    | Neighbor System Name | Neighbor interface    | Neighbor TTL|
|--------------+----------------------+-----------------------+-------------|
| ge100-1/1/1  | dn10-systemR1-fe2    | ge100-2/3/1           | 120         |
| ge100-1/2/1  | dn10-systemR1-fe2    | ge100-2/3/2           | 120         |
| ge100-4/2/1  | dn11-systemR1-fe1    | ge100-1/1/2           | 120         |
| ge100-4/2/2  | dn11-systemR1-fe4    | ge100-4/1/1           | 120         |"""

    expected_result = {
        "ge100-1/1/1": LldpNeighbor("ge100-1/1/1", "dn10-systemR1-fe2", "ge100-2/3/1", 120),
        "ge100-1/2/1": LldpNeighbor("ge100-1/2/1", "dn10-systemR1-fe2", "ge100-2/3/2", 120),
        "ge100-4/2/1": LldpNeighbor("ge100-4/2/1", "dn11-systemR1-fe1", "ge100-1/1/2", 120),
        "ge100-4/2/2": LldpNeighbor("ge100-4/2/2", "dn11-systemR1-fe4", "ge100-4/1/1", 120),
    }

    # Act
    result = DnosLldpDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result


def test_arista_lldp_neighbors_parser():
    # Arrange
    cli_response = json.dumps(
        {
            "lldpNeighbors": [
                {
                    "port": "Ethernet1/1",
                    "neighborDevice": "ar01.site51.cran1.comcast.net",
                    "neighborPort": "HundredGigE0/0/1/0",
                    "ttl": 120,
                },
                {
                    "port": "Ethernet2/1",
                    "neighborDevice": "ar01.site51.cran1.comcast.net",
                    "neighborPort": "HundredGigE0/0/0/11",
                    "ttl": 120,
                },
                {
                    "port": "Ethernet17/1",
                    "neighborDevice": "ar-sc01.site51.cran1.comcast.net",
                    "neighborPort": "FourHundredGigE0/0/0/20",
                    "ttl": 120,
                },
                {
                    "port": "Ethernet18/1",
                    "neighborDevice": "ar-sc01.site51.cran1.comcast.net",
                    "neighborPort": "FourHundredGigE0/0/0/21",
                    "ttl": 120,
                },
                {
                    "port": "Ethernet19/1",
                    "neighborDevice": "tcr02.site2.cran1.comcast.net",
                    "neighborPort": "Ethernet21/1",
                    "ttl": 120,
                },
            ]
        }
    )

    expected_result = {
        "Ethernet1/1": LldpNeighbor(
            "Ethernet1/1",
            "ar01.site51.cran1.comcast.net",
            "HundredGigE0/0/1/0",
            120,
        ),
        "Ethernet2/1": LldpNeighbor(
            "Ethernet2/1",
            "ar01.site51.cran1.comcast.net",
            "HundredGigE0/0/0/11",
            120,
        ),
        "Ethernet17/1": LldpNeighbor(
            "Ethernet17/1",
            "ar-sc01.site51.cran1.comcast.net",
            "FourHundredGigE0/0/0/20",
            120,
        ),
        "Ethernet18/1": LldpNeighbor(
            "Ethernet18/1",
            "ar-sc01.site51.cran1.comcast.net",
            "FourHundredGigE0/0/0/21",
            120,
        ),
        "Ethernet19/1": LldpNeighbor(
            "Ethernet19/1",
            "tcr02.site2.cran1.comcast.net",
            "Ethernet21/1",
            120,
        ),
    }

    # Act
    result = AristaLldpDecipher.decipher(str(cli_response))
    #import pudb; pudb.set_trace()

    # Assert
    assert result == expected_result
