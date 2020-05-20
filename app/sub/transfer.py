from app.db import Transfer


class TransferSubscriber(object):
    @staticmethod
    def handle_transfer(session, block, event, _from, to, value):
        session.add(
            Transfer(
                token_address=event.address,
                block_height=block.height,
                log_index=event.log_index,
                sender=_from,
                receiver=to,
                value=value,
                timestamp=block.time,
                tx_hash=event.tx_hash,
            )
        )

