from automation_utils.helpers.deciphers.drivenets.show_config_protocols_bgp import ShowConfigProtocolsBgpDecipher
from automation_utils.data_objects.config_protocols_bgp import ConfigProtocolsBgp


def test_show_config_protocols_bgp_parser():
    # Arrange
    cli_response = """
    neighbor-group IPV4-LU-ASBR-AR
    neighbor-group IPV4-LU-CRAN-IBONE
    neighbor-group IPV4-LU-RR-SERVER
    neighbor-group IPV4-U-ASBR-AR
      neighbor 96.217.1.14
    neighbor-group IPV4-U-ASBR-RESI-AR
    neighbor-group IPV4-U-CRAN-IBONE
    neighbor-group IPV4-U-RR-SERVER
      neighbor 96.109.183.47
    neighbor-group IPV6-LU-CRAN-IBONE
    neighbor-group IPV6-LU-RR-SERVER
    neighbor-group IPV6-U-ASBR-AR
    neighbor-group IPV6-U-ASBR-RESI-AR
    neighbor-group IPV6-U-CRAN-IBONE
    neighbor-group IPV6-U-RR-SERVER
    """
    
    expected_result = ConfigProtocolsBgp(
        neighbors_ip_addresses = [
            "96.217.1.14",
            "96.109.183.47"
        ]
    )

    # Act
    result = ShowConfigProtocolsBgpDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result
