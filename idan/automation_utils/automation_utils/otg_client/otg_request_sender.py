import re

import requests

import orbital.common as common

logger = common.get_logger(__file__)


class OtgRequestSender:
    _url_regex_pattern = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
    _ip_with_port_regex_pattern = r"(https?:\/\/\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):\d{1,5}\b)"

    def __init__(self, base_url: str):
        if not isinstance(base_url, str) or not self._is_valid_base_url(
            base_url
        ):
            raise ValueError(
                f"[OtgRequestSender__init__] Invalid Base URL - {base_url}. Should be of format: {{ _.scheme }}://{{ _.host IP }}:{{ _.port }}"
            )
        self._base_url = base_url.rstrip("/")
        self._auth_token = None

    def _is_valid_base_url(self, url: str):
        regex = re.compile(self._ip_with_port_regex_pattern, re.IGNORECASE)
        return url is not None and regex.search(url)

    def _is_valid_url(self, url: str):
        regex = re.compile(self._url_regex_pattern, re.IGNORECASE)
        return url is not None and regex.search(url)

    def _send_request(
        self,
        method: str,
        full_url: str,
        body: dict = None,
        headers: dict = None,
        params: dict = None,
    ) -> requests.Response:

        response = requests.request(
            method=method.upper(),
            url=full_url,
            json=body,
            headers=headers,
            params=params,
            timeout=30,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def send_api_request(
        self,
        method: str,
        path: str,
        body: dict | str = None,
        headers: dict = None,
        params: dict = None,
    ) -> requests.Response | dict:
        full_url = f"{self._base_url}{path}"

        if headers is None:
            headers = {"Content-Type": "application/json"}
        try:
            return self._send_request(method, full_url, body, headers, params)
        except requests.exceptions.RequestException as e:
            logger.error(f"[_send_api_request] An error occurred: {e}")
            return None

    # Body should be in {client_id, client_secret, grant_type, scope} format
    def _send_auth_request(
        self,
        auth_url: str,
        body: dict = None,
        headers: dict = None,
        params: dict = None,
    ) -> requests.Response | None:
        if not self._is_valid_url(auth_url):
            raise ValueError(
                f"Invalid authentication provider URL - {auth_url}"
            )
        if headers is None:
            headers = {"Content-Type": "application/json"}

        try:
            return self._send_request("POST", auth_url, body, headers, params)
        except ValueError as e:
            logger.error(f"[_send_auth_request] Error during validation - {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.info(f"[_send_auth_request] An error occurred: {e}")
            return None
