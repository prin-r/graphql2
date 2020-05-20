from app.db import (
    DataSportFeed,
    DataSportFeedRaw,
    DataProvider,
    DataSourceBookkeeping,
)
from app.rpc import rpc
from decimal import Decimal

import sys
import re
import eth_abi


class DataSportFeedRawSubscriber(object):
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

        if bookkeeping is None or bookkeeping.name != "SPORT":
            return

        key_bytes = bytes.fromhex(key[2:])
        key_string = key_bytes.decode("ISO-8859-1").rstrip("\0")

        sport_type = key_string[0:3]
        year = key_string[3:7]
        sport_time = key_string[8:16]
        sport_start_time = "9999"
        home = key_string[17:20]
        away = key_string[21:25]

        sub_keys = key_string.split("/")
        if len(sub_keys) >= 3:
            try:
                year = re.findall(r"\d+", sub_keys[0])[0]
                sport_type = sub_keys[0].replace(year, "")
            except:
                pass

            sport_time = sub_keys[1]

            try:
                [home, away] = sub_keys[2].split("-")
            except:
                pass

            try:
                sport_start_time = sub_keys[3]
            except:
                pass

        dsf = (
            session.query(DataSportFeed)
            .filter_by(sport_type=sport_type)
            .filter_by(year=year)
            .filter_by(sport_time=sport_time)
            .filter_by(sport_start_time=sport_start_time)
            .filter_by(home=home)
            .filter_by(away=away)
            .first()
        )

        try:
            majority_result, status = rpc.QueryInterface(
                data_source.aggregate_contract, block.height
            ).query(key_bytes, value=1000000000000000)
            if status != 1:
                majority_result = [None for i in range(2)]
        except eth_abi.exceptions.InsufficientDataBytes:
            majority_result = [None for i in range(2)]

        if dsf is None:
            session.add(
                DataSportFeed(
                    tcd_address=data_source.tcd_address,
                    sport_type=sport_type,
                    sport_time=sport_time,
                    sport_start_time=sport_start_time,
                    year=year,
                    home=home,
                    away=away,
                    score_home=majority_result[0],
                    score_away=majority_result[1],
                    last_update=block.time,
                )
            )
            session.flush()
        else:
            dsf.score_home = majority_result[0]
            dsf.score_away = majority_result[1]
            dsf.last_update = block.time

        value_bytes32 = value.to_bytes(32, byteorder="big")

        dsfr = (
            session.query(DataSportFeedRaw)
            .filter_by(data_source_address=event.address)
            .filter_by(tcd_address=data_source.tcd_address)
            .filter_by(timestamp=block.time)
            .filter_by(sport_type=sport_type)
            .filter_by(sport_time=sport_time)
            .filter_by(sport_start_time=sport_start_time)
            .filter_by(year=year)
            .filter_by(home=home)
            .filter_by(away=away)
            .first()
        )

        if dsfr is None:
            session.add(
                DataSportFeedRaw(
                    data_source_address=event.address,
                    tcd_address=data_source.tcd_address,
                    timestamp=block.time,
                    sport_type=sport_type,
                    sport_time=sport_time,
                    sport_start_time=sport_start_time,
                    year=year,
                    home=home,
                    away=away,
                    score_home=value_bytes32[0],
                    score_away=value_bytes32[1],
                )
            )
        else:
            dsfr.score_home = value_bytes32[0]
            dsfr.score_away = value_bytes32[1]

