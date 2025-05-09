from automation_utils.helpers.deciphers.common.ip_route import IpRouteDecipher
from automation_utils.data_objects.ip_route import IpRoute, NextHop



def test_ip_route_dnos():
    # Arrange
    cli_response = """
VRF: default
Routing entry for 40.40.40.40/32
  Known via "isis 33287" level 2, priority high, distance 115, metric 301, tag 5, vrf default, best, fib
  Last update 3d01h50m ago, ack
  * 96.217.1.190, via bundle-340
  * 96.217.1.194, via bundle-343
"""
    expected_result = IpRoute(
        destination="40.40.40.40/32",
        protocol="isis 33287",
        next_hops=[
            NextHop("96.217.1.190", interface="bundle-340", is_active=True),
            NextHop("96.217.1.194", interface="bundle-343", is_active=True),
        ],
    )

    # Act
    result = IpRouteDecipher.decipher(cli_response)

    # Assert
    try:
        assert result == expected_result
    except AssertionError:
        print("\nIP Route comparison failed. Details:")
        print(f"\nExpected:\n{expected_result}")
        print(f"\nActual:\n{result}")
        
        if result.destination != expected_result.destination:
            print(f"\nDestination mismatch:")
            print(f"Expected: {expected_result.destination}")
            print(f"Actual: {result.destination}")
            
        if result.protocol != expected_result.protocol:
            print(f"\nProtocol mismatch:")
            print(f"Expected: {expected_result.protocol}")
            print(f"Actual: {result.protocol}")
            
        if result.next_hops != expected_result.next_hops:
            print("\nNext hops mismatch:")
            print("Expected next hops:")
            for hop in expected_result.next_hops:
                print(f"  {hop}")
            print("Actual next hops:")
            for hop in result.next_hops:
                print(f"  {hop}")
        
        raise


def test_ip_route_dnos_recursive():
    # Arrange
    cli_response = """
VRF: default
Routing entry for 1.1.1.0/24
  Known via "bgp", priority low, distance 200, metric 0, vrf default, best, fib
  Last update 04:23:23 ago, ack
    96.109.183.228 (recursive)
  *   96.217.1.205, via bundle-352 label 406040
  *   96.217.0.229, via bundle-178 label 406040
    96.109.183.226 alternate (recursive)
  *   96.217.1.205, via bundle-352 label 406032
  *   96.217.0.229, via bundle-178 label 406032
"""

    expected_result = IpRoute(
        destination="1.1.1.0/24",
        protocol="bgp",
        next_hops=[
            NextHop("96.109.183.228", is_recursive=True),
            NextHop("96.217.1.205", "bundle-352", is_active=True),
            NextHop("96.217.0.229", "bundle-178", is_active=True),
            NextHop("96.109.183.226", is_recursive=True, is_alternate=True),
            NextHop("96.217.1.205", "bundle-352", is_active=True, is_alternate=True),
            NextHop("96.217.0.229", "bundle-178", is_active=True, is_alternate=True),
        ],
    )

    # Act
    result = IpRouteDecipher.decipher(cli_response)

    # Assert
    try:
        assert result == expected_result
    except AssertionError:
        print("\nIP Route comparison failed. Details:")
        print(f"\nExpected:\n{expected_result}")
        print(f"\nActual:\n{result}")
        
        if result.destination != expected_result.destination:
            print(f"\nDestination mismatch:")
            print(f"Expected: {expected_result.destination}")
            print(f"Actual: {result.destination}")
            
        if result.protocol != expected_result.protocol:
            print(f"\nProtocol mismatch:")
            print(f"Expected: {expected_result.protocol}")
            print(f"Actual: {result.protocol}")
            
        if result.next_hops != expected_result.next_hops:
            print("\nNext hops mismatch:")
            print("Expected next hops:")
            for hop in expected_result.next_hops:
                print(f"  {hop}")
            print("Actual next hops:")
            for hop in result.next_hops:
                print(f"  {hop}")
        
        raise


def test_ip_route_dnos_ipv6():
    # Arrange
    cli_response = """
VRF: default
Routing entry for 2001:550:2801::/48
  Known via "bgp", priority low, distance 200, metric 0, vrf default, best, fib
  Last update 04:24:58 ago, ack
    2001:558:4c0:0:3001::30 (recursive)
  *   fe80::8640:76ff:fe3b:39ed, via bundle-178 label 606040
  *   fe80::8640:76ff:fe1e:e5cb, via bundle-352 label 606040
    2001:558:4c0:0:3001::32 alternate (recursive)
  *   fe80::8640:76ff:fe3b:39ed, via bundle-178 label 606032
  *   fe80::8640:76ff:fe1e:e5cb, via bundle-352 label 606032
"""

    expected_result = IpRoute(
        destination="2001:550:2801::/48",
        protocol="bgp",
        next_hops=[
            NextHop("2001:558:4c0:0:3001::30", is_recursive=True),
            NextHop("fe80::8640:76ff:fe3b:39ed", "bundle-178", is_active=True),
            NextHop("fe80::8640:76ff:fe1e:e5cb", "bundle-352", is_active=True),
            NextHop("2001:558:4c0:0:3001::32", is_recursive=True, is_alternate=True),
            NextHop("fe80::8640:76ff:fe3b:39ed", "bundle-178", is_active=True, is_alternate=True),
            NextHop("fe80::8640:76ff:fe1e:e5cb", "bundle-352", is_active=True, is_alternate=True),
        ],
    )

    # Act
    result = IpRouteDecipher.decipher(cli_response)

    # Assert
    try:
        assert result == expected_result
    except AssertionError:
        print("\nIP Route comparison failed. Details:")
        print(f"\nExpected:\n{expected_result}")
        print(f"\nActual:\n{result}")
        
        if result.destination != expected_result.destination:
            print(f"\nDestination mismatch:")
            print(f"Expected: {expected_result.destination}")
            print(f"Actual: {result.destination}")
            
        if result.protocol != expected_result.protocol:
            print(f"\nProtocol mismatch:")
            print(f"Expected: {expected_result.protocol}")
            print(f"Actual: {result.protocol}")
            
        if result.next_hops != expected_result.next_hops:
            print("\nNext hops mismatch:")
            print("Expected next hops:")
            for hop in expected_result.next_hops:
                print(f"  {hop}")
            print("Actual next hops:")
            for hop in result.next_hops:
                print(f"  {hop}")
        
        raise

