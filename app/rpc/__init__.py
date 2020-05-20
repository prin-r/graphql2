import os
import decamelize
import json
import requests

from collections import namedtuple

from eth_utils import function_abi_to_4byte_selector, to_hex, to_bytes
from eth_abi import encode_abi, decode_abi

from pkgutil import get_data

BASE_URL = os.getenv("JSON_RPC_URL")


class RPC(object):
    def __init__(self):
        self.abi = {}
        for file_name in json.loads(get_data("config", "abi_list.json")):
            if file_name.split(".")[-1] != "json":
                continue
            contract_abi = json.loads(get_data("abis", file_name))
            abi_dict = {}
            for fn in contract_abi:
                if "name" in fn:
                    abi_dict[decamelize.convert(fn["name"])] = fn
                else:
                    abi_dict["constructor"] = fn
            self.abi[file_name.split(".")[0]] = abi_dict

    def __getattr__(self, attr):
        def func(address, block_height="latest"):
            if attr not in self.abi:
                raise KeyError("Contract not found")
            return Contract(self.abi[attr], address, block_height)

        return func


class Contract(object):
    def __init__(self, abi, address, block_height="latest"):
        self.abi = abi
        self.address = address
        if block_height != "latest":
            self.block_height = to_hex(block_height)
        else:
            self.block_height = block_height

    def __getattr__(self, attr):
        def func(*args, **kwargs):
            if attr not in self.abi:
                raise ValueError("Function name not match this contract")
            fn = self.abi[attr]
            if len(fn["inputs"]) != len(args):
                raise ValueError("Input not match")
            sig = to_hex(function_abi_to_4byte_selector(fn))

            input_type = [p["type"] for p in fn["inputs"]]
            output_type = [p["type"] for p in fn["outputs"]]
            data = to_hex(encode_abi(input_type, args))
            if "value" in kwargs:
                value = to_hex(kwargs["value"])
            else:
                value = to_hex(0)
            raw_output = requests.post(
                BASE_URL,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [
                        {
                            "to": self.address,
                            "data": sig + data[2:],
                            "value": value,
                        },
                        self.block_height,
                    ],
                    "id": 12,
                },
            ).json()["result"]

            raw_value = decode_abi(output_type, to_bytes(hexstr=raw_output))
            if len(raw_value) == 1:
                return raw_value[0]
            Custom = namedtuple(
                "Custom", [decamelize.convert(p["name"]) for p in fn["outputs"]]
            )
            return Custom._make(raw_value)

        return func


rpc = RPC()
