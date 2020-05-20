from app.db import (
    DataLotteryFeed,
    DataLotteryFeedRaw,
    DataProvider,
    DataSourceBookkeeping,
)
from app.rpc import rpc
from decimal import Decimal

import sys
import eth_abi


class DataLotteryFeedRawSubscriber(object):
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

        if bookkeeping is None or bookkeeping.name != "LOTTERY":
            return

        key_bytes = bytes.fromhex(key[2:])
        key_string = key_bytes.decode("ISO-8859-1").rstrip("\0")

        lottery_type = key_string[0:3]
        lottery_time = key_string[4:]

        dlf = (
            session.query(DataLotteryFeed)
            .filter_by(lottery_type=lottery_type)
            .filter_by(lottery_time=lottery_time)
            .first()
        )

        try:
            majority_result, status = rpc.QueryInterface(
                data_source.aggregate_contract, block.height
            ).query(key_bytes, value=1000000000000000)
            if status != 1:
                majority_result = [None for i in range(7)]
        except eth_abi.exceptions.InsufficientDataBytes:
            majority_result = [None for i in range(7)]

        if dlf is None:
            session.add(
                DataLotteryFeed(
                    tcd_address=data_source.tcd_address,
                    lottery_type=lottery_type,
                    lottery_time=lottery_time,
                    white_ball_1=majority_result[0],
                    white_ball_2=majority_result[1],
                    white_ball_3=majority_result[2],
                    white_ball_4=majority_result[3],
                    white_ball_5=majority_result[4],
                    red_ball=majority_result[5],
                    mul=majority_result[6],
                    last_update=block.time,
                )
            )
            session.flush()
        else:
            dlf.white_ball_1 = majority_result[0]
            dlf.white_ball_2 = majority_result[1]
            dlf.white_ball_3 = majority_result[2]
            dlf.white_ball_4 = majority_result[3]
            dlf.white_ball_5 = majority_result[4]
            dlf.red_ball = majority_result[5]
            dlf.mul = majority_result[6]
            dlf.last_update = block.time

        value_bytes32 = value.to_bytes(32, byteorder="big")

        dlfr = (
            session.query(DataLotteryFeedRaw)
            .filter_by(data_source_address=event.address)
            .filter_by(tcd_address=data_source.tcd_address)
            .filter_by(timestamp=block.time)
            .filter_by(lottery_type=lottery_type)
            .filter_by(lottery_time=lottery_time)
            .first()
        )

        if dlfr is None:
            session.add(
                DataLotteryFeedRaw(
                    data_source_address=event.address,
                    tcd_address=data_source.tcd_address,
                    timestamp=block.time,
                    lottery_type=lottery_type,
                    lottery_time=lottery_time,
                    white_ball_1=value_bytes32[0],
                    white_ball_2=value_bytes32[1],
                    white_ball_3=value_bytes32[2],
                    white_ball_4=value_bytes32[3],
                    white_ball_5=value_bytes32[4],
                    red_ball=value_bytes32[5],
                    mul=value_bytes32[6],
                )
            )
        else:
            dlfr.white_ball_1 = value_bytes32[0]
            dlfr.white_ball_2 = value_bytes32[1]
            dlfr.white_ball_3 = value_bytes32[2]
            dlfr.white_ball_4 = value_bytes32[3]
            dlfr.white_ball_5 = value_bytes32[4]
            dlfr.red_ball = value_bytes32[5]
            dlfr.mul = value_bytes32[6]

