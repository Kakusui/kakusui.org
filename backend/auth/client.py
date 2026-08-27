## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import os
from ipaddress import ip_address, ip_network

from fastapi import Request


IS_FLY_RUNTIME = bool(os.environ.get("FLY_APP_NAME") or os.environ.get("FLY_MACHINE_ID"))

# Fly-Client-IP identifies the immediate client accepted by Fly Proxy. When
# that address is an official Cloudflare edge, CF-Connecting-IP is the next
# authenticated hop. Unknown/new edge ranges safely fall back to the edge IP.
# Source: https://www.cloudflare.com/ips/
_CLOUDFLARE_NETWORKS = tuple(
    ip_network(network)
    for network in (
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
        "162.158.0.0/15",
        "104.16.0.0/13",
        "104.24.0.0/14",
        "172.64.0.0/13",
        "131.0.72.0/22",
        "2400:cb00::/32",
        "2606:4700::/32",
        "2803:f800::/32",
        "2405:b500::/32",
        "2405:8100::/32",
        "2a06:98c0::/29",
        "2c0f:f248::/32",
    )
)


def _parse_address(value: str | None):
    if value is None:
        return None
    try:
        return ip_address(value.strip())
    except ValueError:
        return None


def get_request_client_ip(request: Request) -> str | None:
    peer = _parse_address(request.client.host if request.client is not None else None)
    if not IS_FLY_RUNTIME:
        return str(peer) if peer is not None else None

    # Public HTTP services on Fly cannot bypass Fly Proxy, which overwrites
    # this platform header. Never trust generic X-Forwarded-For here.
    fly_client = _parse_address(request.headers.get("Fly-Client-IP"))
    if fly_client is None:
        return str(peer) if peer is not None else None

    if any(fly_client in network for network in _CLOUDFLARE_NETWORKS):
        cloudflare_client = _parse_address(request.headers.get("CF-Connecting-IP"))
        if cloudflare_client is not None:
            return str(cloudflare_client)

    return str(fly_client)


def get_request_client_identifier(request: Request) -> str:
    client_ip = _parse_address(get_request_client_ip(request))
    if client_ip is None:
        return "unknown"
    if client_ip.version == 6 and client_ip.ipv4_mapped is not None:
        return str(client_ip.ipv4_mapped)
    if client_ip.version == 6:
        source_network = ip_network(f"{client_ip}/64", strict=False)
        return f"{source_network.network_address}/64"
    return str(client_ip)
