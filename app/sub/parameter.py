from app.db import Parameter
from app.utils.ipfs import get_ipfs_hash, get_string
from app.sub.tcd import update_list

from eth_utils import to_hex


class ParameterSubscriber(object):
    @staticmethod
    def handle_parameter_changed(session, block, event, key, value):
        parameter = session.query(Parameter).get(event.address)
        string_key = bytes.fromhex(key[2:]).decode("utf-8").replace("\x00", "")

        new_dict = dict(parameter.current_parameters)
        new_dict[string_key] = str(value)
        parameter.current_parameters = new_dict
        session.add(parameter)

        # Update tcd info
        token = parameter.token
        if string_key == "data:min_provider_stake":
            for data_source in token.tcds:
                data_source.min_stake = int(value)
                session.add(data_source)
        elif string_key == "data:max_provider_count":
            for data_source in token.tcds:
                data_source.max_provider_count = int(value)
                session.add(data_source)

