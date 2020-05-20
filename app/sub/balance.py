from app.db import Balance


class BalanceSubscriber(object):
    @staticmethod
    def handle_transfer(session, block, event, _from, to, value):
        value = int(value)
        if _from != "0x0000000000000000000000000000000000000000":
            ident = (event.address, _from)
            balance = session.query(Balance).get(ident)
            if balance is None:
                balance = Balance(
                    token_address=event.address,
                    user=_from,
                    value=0,
                    locked_value=0,
                )
            balance.value -= value
            if balance.value == 0:
                session.delete(balance)
            else:
                session.add(balance)

        if to != "0x0000000000000000000000000000000000000000":
            ident = (event.address, to)
            balance = session.query(Balance).get(ident)
            if balance is None:
                balance = Balance(
                    token_address=event.address,
                    user=to,
                    value=0,
                    locked_value=0,
                )
            balance.value += value
            if balance.value == 0:
                session.delete(balance)
            else:
                session.add(balance)

