from app.db import DataRead, TCD

from decimal import Decimal

import sys


class DataReadSubscriber(object):
    @staticmethod
    def handle_data_read(session, block, event, reader, key):
        tcd = session.query(TCD).filter_by(address=event.address).first()
        if tcd is None:
            return

        key_bytes = bytes.fromhex(key[2:])
        key_string = key_bytes.decode("utf-8").rstrip("\0")

        dr = (
            session.query(DataRead)
            .filter_by(reader_address=reader)
            .filter_by(key=key_string)
            .filter_by(timestamp=block.time)
            .filter_by(log_index=event.log_index)
            .filter_by(tcd_address=tcd.address)
            .first()
        )
        if dr is None:
            session.add(
                DataRead(
                    reader_address=reader,
                    key=key_string,
                    timestamp=block.time,
                    log_index=event.log_index,
                    tcd_address=tcd.address,
                )
            )

