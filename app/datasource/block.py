class BlockInfo(object):
    def __init__(self, block_id, block_hash, block_time):
        self.height = block_id
        self.hash = block_hash
        self.time = block_time

    def __repr__(self):
        return f"BlockInfo(height={self.height},hash={self.hash},time={self.time})"


class EventInfo(object):
    def __init__(self, log_index, tx_hash, event_name, event_address, event_params):
        self.log_index = log_index
        self.tx_hash = tx_hash
        self.name = event_name
        self.address = event_address
        self.params = event_params

    def __repr__(self):
        return f"EventInfo(log_index={self.log_index},tx_hash={self.tx_hash},name={self.name}),address={self.address}),params={self.params})"


class Block(object):
    def __init__(self, block_info, events):
        self.block_info = block_info
        self.events = events
