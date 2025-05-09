import json
from automation_utils.helpers.deciphers.drivenets.isis_neighbors import (
    IsisNeighborsDecipher as DnosNeighborsDecipher,
    IsisConfigDecipher as DnosIsisConfigDecipher,
)
from automation_utils.helpers.deciphers.arista.isis_neighbors import (
    IsisNeighborsDecipher as AristaNeighborsDecipher,
)
from automation_utils.data_objects.isis_neighbors import (
    IsisNeighbors,
    IsisNeighbor,
)


def test_isis_config():
    output = """
# tcr02.siteA.cran1 config-start [16-Dec-2024 21:22:15 UTC]

protocols
  isis
    maximum-adjacencies 500 threshold 75
    maximum-routes 1000000 threshold 75
    nsr disabled
    instance 33287
      advertise max-metric disabled
      advertise overload-bit disabled
      authentication level level-2 snp-auth sign-validate
      authentication level level-2 type md5 password enc-gAAAAABjXXXJlaMZt7SYQ5uMfhR_e18iH5__zx1yTt-w3HqCDO1DTr-n6_JtgtIBIW9NslQ6GVdhF6x9ZbAGHibxnovvS3fa2g==
      dynamic-hostname enabled
      iso-network 49.0000.0961.0918.3049.00
      level level-2
      lsp-mtu 1492
      max-metric 16777214
      address-family ipv4-unicast
        maximum-paths 32
        prefix-priority high tag 5
        traffic-engineering level level-2 enabled
        microloop-avoidance
          admin-state enabled
          fib-delay 3000
        !
        segment-routing
          admin-state enabled
        !
        ti-fast-reroute
          admin-state enabled
          protection-mode link
        !
        timers
          throttle spf delay 50 max-holdtime 2000 min-holdtime 100
        !
      !
      address-family ipv6-unicast
        maximum-paths 32
        prefix-priority high tag 5
        topology enabled
        traffic-engineering level level-2 enabled
        microloop-avoidance
          admin-state enabled
          fib-delay 3000
        !
        segment-routing
          admin-state enabled
        !
        ti-fast-reroute
          admin-state enabled
          protection-mode link
        !
        timers
          throttle spf delay 50 max-holdtime 2000 min-holdtime 100
        !
      !
      flex-algo
        use-legacy-te disabled
        participate 128
        !
      !
      interface lo0
        address-family ipv4-unicast
          metric level level-2 1
          prefix-sid flex-algo 128 label 406652 prefix-type node
          prefix-sid label 406152 prefix-type node
          tag level level-2 5
        !
      !
      interface lo60
        address-family ipv6-unicast
          metric level level-2 1
          prefix-sid flex-algo 128 label 606652 prefix-type node
          prefix-sid label 606152 prefix-type node
          tag level level-2 5
        !
      !
      interface lo999
        address-family ipv4-unicast
          metric level level-2 1
        !
        address-family ipv6-unicast
          metric level level-2 1
        !
      !
      interface bundle-340
        authentication md5 password enc-gAAAAABjXXXJlaMZt7SYQ5uMfhR_e18iH5__zx1yTt-w3HqCDO1DTr-n6_JtgtIBIW9NslQ6GVdhF6x9ZbAGHibxnovvS3fa2g==
        level level-2
        network-type point-to-point
        address-family ipv4-unicast
          fast-reroute backup-candidate enabled
          metric level level-2 100
        !
        address-family ipv6-unicast
          fast-reroute backup-candidate enabled
          metric level level-2 100
        !
        delay-normalization
          interval 10
          offset 0
        !
      !
      interface bundle-721
        authentication md5 password enc-gAAAAABjXXXJlaMZt7SYQ5uMfhR_e18iH5__zx1yTt-w3HqCDO1DTr-n6_JtgtIBIW9NslQ6GVdhF6x9ZbAGHibxnovvS3fa2g==
        level level-2
        network-type point-to-point
        address-family ipv4-unicast
          fast-reroute backup-candidate enabled
          metric level level-2 100
        !
        address-family ipv6-unicast
          fast-reroute backup-candidate enabled
          metric level level-2 100
        !
        delay-normalization
          interval 10
          offset 0
        !
      !
      overload on-startup
        admin-state enabled
        advertisement-type overload-bit
        wait-for-bgp
      !
      timers
        lsp-interval 0
        lsp-lifetime 4000
        lsp-refresh 3600
        throttle lsp delay 0 max-holdtime 2000 min-holdtime 200
      !
    !
  !
!

    """
    isis_config = DnosIsisConfigDecipher.decipher(output)
    assert isis_config == {'bundle-340', 'bundle-721'}, "Bundle IDs do not match expected values."


def test_dnos_isis_neighbors_parser():
    # Arrange
    cli_response = """Instance 33287:
  System Id                      Interface               Level  State         Last State Change    Holdtime  SNPA            
  scr01.site7.cran1              bundle-349              L2     Up            1w4d3h25m40s         22        point-to-point  
  re0-msc01.site9.cran1          bundle-247              L2     Up            1w4d5h52m9s          21        point-to-point  
  tcr01.site10.cran1             bundle-178              L2     Up            2d2h56m11s           28        point-to-point"""

    expected_result = IsisNeighbors(
        instance_id=33287,
        neighbors={
            "bundle-349":
            IsisNeighbor(
                    system_name="scr01.site7.cran1",
                    interface_name="bundle-349",
                    state="Up",
                    last_change="1w4d3h25m40s",
            ),
            "bundle-247":
            IsisNeighbor(
                system_name="re0-msc01.site9.cran1",
                interface_name="bundle-247",
                state="Up",
                last_change="1w4d5h52m9s",
            ),
            "bundle-178":
            IsisNeighbor(
                system_name="tcr01.site10.cran1",
                interface_name="bundle-178",
                state="Up",
                last_change="2d2h56m11s",
            ),
        },
    )

    # Act
    result = DnosNeighborsDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result


def test_arista_isis_neighbors_parser():
    # Arrange
    cli_response = json.dumps(
        {
            "vrfs": {
                "default": {
                    "isisInstances": {
                        "33287": {
                            "neighbors": {
                                "0961.0905.1222": {
                                    "adjacencies": [
                                        {
                                            "hostname": "patcrla700",
                                            "circuitId": "72",
                                            "interfaceName": "Port-Channel766",
                                            "state": "up",
                                            "lastHelloTime": 1733239696,
                                            "snpa": "P2P",
                                            "level": "level-2",
                                            "details": {
                                                "advertisedHoldTime": 30,
                                                "stateChanged": 1733068984,
                                                "interfaceAddressFamily": "both",
                                                "neighborAddressFamily": "both",
                                                "ip4Address": "96.217.3.242",
                                                "ip6Address": "fe80::ae3d:94ff:febb:e222",
                                                "areaIds": ["49.0000"],
                                                "bfdIpv4State": "adminDown",
                                                "bfdIpv6State": "adminDown",
                                                "srEnabled": False,
                                                "grSupported": "Supported",
                                                "grState": "",
                                            },
                                            "routerIdV4": "0.0.0.0",
                                        }
                                    ]
                                },
                                "0961.0905.1223": {
                                    "adjacencies": [
                                        {
                                            "hostname": "patcrlb700",
                                            "circuitId": "26",
                                            "interfaceName": "Port-Channel769",
                                            "state": "up",
                                            "lastHelloTime": 1733239696,
                                            "snpa": "P2P",
                                            "level": "level-2",
                                            "details": {
                                                "advertisedHoldTime": 30,
                                                "stateChanged": 1733068985,
                                                "interfaceAddressFamily": "both",
                                                "neighborAddressFamily": "both",
                                                "ip4Address": "96.217.3.246",
                                                "ip6Address": "fe80::d6af:f7ff:feca:146f",
                                                "areaIds": ["49.0000"],
                                                "bfdIpv4State": "adminDown",
                                                "bfdIpv6State": "adminDown",
                                                "srEnabled": False,
                                                "grSupported": "Supported",
                                                "grState": "",
                                            },
                                            "routerIdV4": "0.0.0.0",
                                        }
                                    ]
                                },
                            }
                        }
                    }
                }
            }
        }
    )

    expected_result = IsisNeighbors(
        instance_id=33287,
        neighbors={
            "Port-Channel766":
            IsisNeighbor(
                system_name="patcrla700",
                interface_name="Port-Channel766",
                state="up",
                last_change="1733068984",
            ),
            "Port-Channel769":
            IsisNeighbor(
                system_name="patcrlb700",
                interface_name="Port-Channel769",
                state="up",
                last_change="1733068985",
            ),
        },
    )

    # Act
    result = AristaNeighborsDecipher.decipher(cli_response)

    # Assert
    assert result == expected_result
