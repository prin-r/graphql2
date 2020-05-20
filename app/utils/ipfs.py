import ipfsapi
from base58 import b58encode

from eth_utils import remove_0x_prefix, to_bytes

client = ipfsapi.connect("https://ipfs.bandprotocol.com", 443)


def get_json(hex_string):
    try:
        return client.get_json(get_ipfs_hash(hex_string))
    except:
        return None


def get_string(hex_string):
    try:
        return client.cat(get_ipfs_hash(hex_string)).decode("utf-8")
    except:
        return None


def get_ipfs_hash(hex_string):
    hex_string = remove_0x_prefix(hex_string)
    pad_hex_string = hex_string.rjust(64, "0")
    return b58encode(to_bytes(hexstr="1220" + pad_hex_string))
