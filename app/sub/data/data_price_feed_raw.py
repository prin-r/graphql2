from app.db import (
    DataPriceFeed,
    DataPriceFeedRaw,
    DataProvider,
    DataSourceBookkeeping,
)
from app.rpc import rpc

from decimal import Decimal

import sys
import eth_abi


class DataPriceFeedRawSubscriber(object):
    @staticmethod
    def handle_data_point_set(session, block, event, key, value):

        data_source = (
            session.query(DataProvider)
            .filter_by(data_source_address=event.address)
            .first()
        )
        if data_source is None:
            return

        bookkeeping = (
            session.query(DataSourceBookkeeping)
            .filter_by(address=data_source.tcd_address)
            .first()
        )
        if bookkeeping is None or bookkeeping.name != "PRICE":
            return

        key_bytes = bytes.fromhex(key[2:])
        key_string = key_bytes.decode("ISO-8859-1").rstrip("\0")

        dpf = session.query(DataPriceFeed).filter_by(pair=key_string).first()

        try:
            median_price, status = rpc.QueryInterface(
                data_source.aggregate_contract, block.height
            ).query(key_bytes, value=1000000000000000)
            if status != 1:
                median_price = None
            else:
                median_price = int(median_price.hex(), 16)
        except eth_abi.exceptions.InsufficientDataBytes:
            median_price = None

        if dpf is None:
            session.add(
                DataPriceFeed(
                    pair=key_string,
                    tcd_address=data_source.tcd_address,
                    value=median_price,
                    last_update=block.time,
                )
            )
            session.flush()
        else:
            dpf.value = median_price
            dpf.last_update = block.time

        dpfr = (
            session.query(DataPriceFeedRaw)
            .filter_by(data_source_address=event.address)
            .filter_by(tcd_address=data_source.tcd_address)
            .filter_by(timestamp=block.time)
            .filter_by(pair=key_string)
            .first()
        )

        if dpfr is None:
            session.add(
                DataPriceFeedRaw(
                    data_source_address=event.address,
                    tcd_address=data_source.tcd_address,
                    timestamp=block.time,
                    pair=key_string,
                    value=value,
                )
            )
        else:
            dpfr.value

