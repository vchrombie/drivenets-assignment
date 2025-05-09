import re

from automation_utils.data_objects.ping_data import (
    Status,
    PingData,
    PingResponse,
)
from automation_utils.helpers.deciphers.decipher_base import Decipher

"""PING 1.1.1.1 (1.1.1.1) from 1.1.1.1 : 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=64 time=0.122 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=64 time=0.110 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=64 time=0.092 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=64 time=0.094 ms
64 bytes from 1.1.1.1: icmp_seq=5 ttl=64 time=0.101 ms

--- 1.1.1.1 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4077ms
rtt min/avg/max/mdev = 0.092/0.103/0.122/0.011 ms"""


class DnosPingDecipher(Decipher):
    @staticmethod
    def decipher(cli_response: str) -> PingData:
        ping_data = PingData()
        ret, destination_ip, responses = DnosPingDecipher.parse_raw_response(
            cli_response
        )
        if ret:
            ping_data.status = Status(name="ERROR", value=ret)
            ping_data.result_message = cli_response
        else:
            summary = DnosPingDecipher.parse_summary_line(
                cli_response, destination_ip
            )

            if summary is not None:
                ping_data.status = Status(name="OK", value=ret)
                summary_index = (
                    list(responses)[-1] + 1 if responses else None
                )  # extract last index and forward 1

                if summary_index:
                    responses[summary_index] = summary
                else:
                    # if threre is no index, create one
                    summary_indexed = {}
                    summary_indexed[0] = summary
                    responses = summary_indexed
                ping_data.responses = responses
            else:
                ping_data.status = Status(name="ERROR", value=ret)
                ping_data.result_message = cli_response
        return ping_data

    @staticmethod
    def _arrange_response_line(parsed_dict, is_summary=False):
        """
        gNOI message:

        message PingResponse {
            string source = 1
            // Source of received bytes.
            int64 time = 2

            int32 sent = 3
            // Total packets sent.
            int32 received = 4
            // Total packets received.
            int64 min-time = 5
            // Minimum round trip time in nanoseconds.
            int64 avg-time = 6
            // Average round trip time in nanoseconds.
            int64 max-time = 7
            // Maximum round trip time in nanoseconds.
            int64 std-dev = 8
            // Standard deviation in round trip time.

            int32 bytes = 11
            // Bytes received.
            int32 sequence = 12
            // Sequence number of received packet.
            int32 ttl = 13
            // Remaining time to live value.}
        """

        if not is_summary:
            # echo
            ping_response = PingResponse(
                source=parsed_dict["source"],
                time=parsed_dict["time"] if "time" in parsed_dict else 0,
                sent=0,
                received=0,
                min_time=0,
                avg_time=0,
                max_time=0,
                std_dev=0,
                bytes=parsed_dict["bytes"],
                sequence=parsed_dict["sequence"],
                ttl=parsed_dict["ttl"],
            )
        else:
            # summary
            ping_response = PingResponse(
                source=parsed_dict["source"],
                time=0,
                sent=parsed_dict["sent"],
                received=parsed_dict["received"],
                min_time=(
                    parsed_dict["min_time"] if "min_time" in parsed_dict else 0
                ),
                avg_time=(
                    parsed_dict["avg_time"] if "avg_time" in parsed_dict else 0
                ),
                max_time=(
                    parsed_dict["max_time"] if "max_time" in parsed_dict else 0
                ),
                std_dev=(
                    parsed_dict["std_dev"] if "std_dev" in parsed_dict else 0
                ),
                bytes=0,
                sequence=0,
                ttl=0,
            )
        return ping_response

    @staticmethod
    def parse_raw_response(buffer):
        # header line of PING (line 1 , must)- if it exists, we assume the ping operation was executed (regardless of result)
        header = re.compile(
            r"(/s+)?PING (?P<NAME>\S+)(\s+)?\((?P<IPD>\S+)\) (from (?P<IPS>\S+) (.*)?:)?"
        )

        # compile a regular expression from ping line : "64 bytes from 2.2.2.2: icmp_seq=1 ttl=64 time=0.139 ms"
        #                                                bytes         source   sequence   ttl    time"
        pattern = re.compile(
            "(?P<bytes>.*) bytes from (?P<source>.*): icmp_seq=(?P<sequence>.*) ttl=(?P<ttl>.*) time=(?P<time>.*) ms"
        )

        # this patters inrequired in case size < 16 , as the time field is NOT appearing in this case.
        pattern1 = re.compile(
            "(?P<bytes>.*) bytes from (?P<source>.*): icmp_seq=(?P<sequence>.*) ttl=(?P<ttl>.*)"
        )
        index = 0
        check_header = True
        dest_ip = None
        ping_list_responses = {}
        for line in buffer.splitlines():
            if check_header:
                header_line = header.match(line)
                if not header_line:
                    return 1, None, None
                check_header = False
                parsed_header = header_line.groupdict()
                dest_ip = parsed_header["IPD"]
                continue

            parsed_line = pattern.match(line)
            if not parsed_line:
                parsed_line = pattern1.match(line)
            if parsed_line:
                parsed_dict = parsed_line.groupdict()

                ping_list_responses[index] = (
                    DnosPingDecipher._arrange_response_line(parsed_dict)
                )
                index = index + 1

        if ping_list_responses:
            return 0, dest_ip, ping_list_responses
        else:
            return 0, dest_ip, None

    @staticmethod
    def parse_summary_line(buffer, source):
        # compile a regular expression from ping line : "5 packets transmitted, 5 received"
        #                                                sent                   received
        pattern = re.compile(
            "(?P<sent>.*) packets transmitted, (?P<received>.*) received.*"
        )
        # compile a regular expression from ping line : "rtt min / avg / max / mdev = 5.041 / 5.101 / 5.171 / 0.043 ms"
        #                                                  min_time avg_time max_time std_dev
        # NOTE! , this line maybe missing if size < 16
        pattern1 = re.compile(
            "rtt min/avg/max/mdev = (?P<min_time>.*)/(?P<avg_time>.*)/(?P<max_time>.*)/(?P<std_dev>.*) ms"
        )

        ping_parsed_dict = {"source": source}
        for line in buffer.splitlines():
            parsed_line = pattern.match(line)
            if not parsed_line:
                parsed_line = pattern1.match(line)
            if parsed_line:
                parsed_dict = parsed_line.groupdict()
                ping_parsed_dict.update(parsed_dict)
        return (
            DnosPingDecipher._arrange_response_line(ping_parsed_dict, True)
            if ping_parsed_dict
            else None
        )
