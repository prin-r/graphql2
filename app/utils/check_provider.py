import requests
import os
from eth_utils import keccak, remove_0x_prefix

BASE_URL = os.getenv("JSON_RPC_URL")


def next_address_list(tcd_address, is_active, key, height):
    slot = "0" * 63 + "2" if is_active else "0" * 63 + "3"
    location = "0x" + remove_0x_prefix(key).rjust(64, "0") + slot
    raw_output = requests.post(
        BASE_URL,
        json={
            "jsonrpc": "2.0",
            "method": "eth_getStorageAt",
            "params": [
                tcd_address,
                "0x" + keccak(hexstr=location).hex(),
                height,
            ],
            "id": 12,
        },
    )
    return raw_output.json()["result"]


def get_token_lock(tcd_address, provider_address, participant, height):
    location = (
        "0x"
        + remove_0x_prefix(provider_address).rjust(64, "0")
        + "0" * 63
        + "1"
    )
    map_base = hex(int("0x" + keccak(hexstr=location).hex(), 0) + 3)
    new_location = (
        "0x"
        + remove_0x_prefix(participant).rjust(64, "0")
        + remove_0x_prefix(map_base).rjust(64, "0")
    )
    raw_output = requests.post(
        BASE_URL,
        json={
            "jsonrpc": "2.0",
            "method": "eth_getStorageAt",
            "params": [
                tcd_address,
                "0x" + keccak(hexstr=new_location).hex(),
                height,
            ],
            "id": 12,
        },
    )

    print("------------------------", flush=True)
    print(raw_output.json(), flush=True)
    return int(raw_output.json()["result"], 0)

