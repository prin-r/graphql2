import decamelize
import keyword
import time
import json

from app.sub import ALL_SUBSRIBERS
from app.db import Contract, DataSourceBookkeeping, Block as BlockDB, Token
from app.version import versioned_session
from app.rpc import rpc

from datetime import datetime
from sqlalchemy import (
    create_engine,
    select,
    Column,
    String,
    Table,
    MetaData,
    Integer,
)
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from web3 import Web3, HTTPProvider
from web3.utils.events import event_abi_to_log_topic
from web3.utils.events import get_event_data
from web3.utils.normalizers import to_checksum_address
from eth_utils import to_hex, to_checksum_address
from app.datasource.block import Block, BlockInfo, EventInfo
from app.version import revert

from pkgutil import get_data

TIMED = False


def with_time(f):
    def wrap(*args, **kwargs):
        start_time = datetime.now()
        result = f(*args, **kwargs)
        end_time = datetime.now()
        if TIMED:
            print(f.__name__, "used", end_time - start_time)
        return result

    return wrap


class SubscriberManager(object):
    @with_time
    def on_block(self, session, block_info, events):
        contracts = set([c.address for c in session.query(Contract).all()])
        for event in events:
            event.handler = f"handle_{decamelize.convert(event.name)}"
            params = event.params
            for key, value in list(params.items()):
                del params[key]
                if keyword.iskeyword(key):
                    key = f"_{key}"
                if isinstance(value, bytes):
                    value = f"0x{value.hex()}"
                params[decamelize.convert(key)] = value
        for subscriber in ALL_SUBSRIBERS:
            if hasattr(subscriber, "handle_begin_block"):
                getattr(subscriber, "handle_begin_block")(session, block_info)
            for event in events:
                if event.address not in contracts:
                    continue
                if hasattr(subscriber, event.handler):
                    getattr(subscriber, event.handler)(
                        session, block_info, event, **event.params
                    )
                    contracts = set(
                        [c.address for c in session.query(Contract).all()]
                    )
            session.flush()


class Looper(object):
    def __init__(self, database):
        self.database = database
        self.sub_manager = SubscriberManager()
        self.abi = self.load_events_from_abis()
        genesis = json.loads(get_data("config", "config.json"))
        self.event_engine = create_engine(genesis["eventDBHost"], echo=False)
        metadata = MetaData(self.event_engine)
        self.event_table = Table(
            "block",
            metadata,
            Column("height", Integer, primary_key=True),
            Column("block_hash", String, nullable=False),
            Column("parent_hash", String),
            Column("event_addresses", ARRAY(String), nullable=False),
            Column("event_logs", JSON, nullable=False),
            Column("timestamp", Integer, nullable=False),
        )

    def init(self):
        # print("START INIT")
        session = self.database.get_session()
        genesis = json.loads(get_data("config", "config.json"))
        session.add(
            BlockDB(
                height=genesis["blockId"],
                hash=genesis["blockHash"],
                parent_hash=genesis["blockParentHash"],
                block_time=genesis["blockTime"],
            )
        )
        band_registry = genesis["bandRegistry"]
        session.add(
            Contract(address=band_registry, contract_type="BAND_REGISTRY")
        )
        band_address = to_checksum_address(
            rpc.BandRegistry(band_registry).band()
        )

        session.add(
            Token(
                address=band_address,
                total_supply=0,
                name="BAND",
                symbol="BND",
                decimals=18,
            )
        )
        session.add(Contract(address=band_address, contract_type="BAND_TOKEN"))
        session.add(
            Contract(
                address=genesis["CommunityFactory"], contract_type="COM_FACTORY"
            )
        )
        session.add(
            Contract(
                address=genesis["AggTCDFactory"], contract_type="AGGTCD_FACTORY"
            )
        )
        session.add(
            Contract(
                address=genesis["MultiSigTCDFactory"],
                contract_type="MULTI_SIG_TCD_FACTORY",
            )
        )
        session.add(
            Contract(
                address=genesis["OffchainAggTCDFactory"],
                contract_type="OFFCHAIN_AGG_TCD_FACTORY",
            )
        )
        session.add(
            Contract(address=genesis["TCRFactory"], contract_type="TCR_FACTORY")
        )
        # if "DataSourceBookkeepingPriceAddress" in genesis:
        #     for address in genesis["DataSourceBookkeepingPriceAddress"]:
        #         session.add(
        #             DataSourceBookkeeping(address=address, name="PRICE")
        #         )
        # if "DataSourceBookkeepingLotteryAddress" in genesis:
        #     for address in genesis["DataSourceBookkeepingLotteryAddress"]:
        #         session.add(
        #             DataSourceBookkeeping(address=address, name="LOTTERY")
        #         )
        # if "DataSourceBookkeepingSportAddress" in genesis:
        #     for address in genesis["DataSourceBookkeepingSportAddress"]:
        #         session.add(
        #             DataSourceBookkeeping(address=address, name="SPORT")
        #         )

        session.commit()
        print(genesis["blockId"])

    def load_events_from_abis(self):
        abi_list = []
        for file_name in json.loads(get_data("config", "abi_list.json")):
            if file_name.split(".")[-1] != "json":
                continue
            abi_list += json.loads(get_data("abis", file_name))
        events = [abi for abi in abi_list if abi["type"] == "event"]
        abi_map = {}
        for event in events:
            abi_map[event_abi_to_log_topic(event)] = event
        return abi_map

    @with_time
    def get_blocks_by_number(self, current_block_height):
        blocks = self.event_engine.execute(
            select([self.event_table])
            .where(current_block_height - 10 <= self.event_table.c.height)
            .where(self.event_table.c.height <= current_block_height + 1000)
        )
        data = {}
        for block in blocks:
            data[block.height] = block
        return data

    @with_time
    def get_event_from_logs(self, logs):
        events = []
        for log in logs:
            if log["data"] is None or not log["topics"]:
                continue

            log["topics"] = [
                bytes.fromhex(topic[2:]) for topic in log["topics"]
            ]
            if log["topics"][0] not in self.abi:
                continue

            num_logs = 1
            for e in self.abi[log["topics"][0]]["inputs"]:
                if e["indexed"]:
                    num_logs += 1

            if len(log["topics"]) != num_logs:
                continue

            log["data"] = bytes.fromhex(log["data"][2:])

            event = get_event_data(self.abi[log["topics"][0]], log)
            events.append(
                EventInfo(
                    int(log["logIndex"], 0),
                    log["transactionHash"],
                    event["event"],
                    to_checksum_address(log["address"]),
                    dict(event["args"]),
                )
            )
        return events

    @with_time
    def run(self):
        # print("START RUN")
        try:
            session = versioned_session(self.database.get_session())
            latest_block_in_db = (
                session.query(BlockDB).order_by(BlockDB.height.desc()).first()
            )
            if latest_block_in_db is None:
                raise ValueError("Not found row in DB")

            blocks = self.get_blocks_by_number(latest_block_in_db.height)
            current_height = latest_block_in_db.height
            while current_height in blocks:
                current_block = session.query(BlockDB).get(current_height)
                if current_block.hash != blocks[current_height].block_hash:
                    current_height -= 1
                    # print(
                    #     "fork detected at block ",
                    #     current_height,
                    #     ", hash from db is",
                    #     current_block.hash,
                    #     ", hash from event is",
                    #     blocks[current_height].block_hash,
                    # )
                    revert(session)
                else:
                    break

            if current_height not in blocks:
                raise ValueError("Revert more than 10 block something wrong")

            current_height += 1
            while current_height in blocks:
                session.rollback()
                block = blocks[current_height]
                # print(
                #     "blockNumber:", current_height, ",blockHash:", block.block_hash
                # )
                # save block
                session.add(
                    BlockDB(
                        height=current_height,
                        hash=block.block_hash,
                        parent_hash=block.parent_hash,
                        block_time=block.timestamp,
                    )
                )

                contracts = set(
                    [c.address.lower() for c in session.query(Contract).all()]
                )
                event_contracts = set(block.event_addresses)
                # print(contracts, event_contracts)
                if contracts.intersection(event_contracts):
                    self.sub_manager.on_block(
                        session,
                        BlockInfo(
                            current_height, block.block_hash, block.timestamp
                        ),
                        self.get_event_from_logs(block.event_logs),
                    )
                session.commit()

                current_height += 1

            print(current_height - 1)
        finally:
            session.rollback()

    @with_time
    def loop(self):
        self.init()
        while True:
            self.run()
            time.sleep(1)

