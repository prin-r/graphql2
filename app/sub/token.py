from app.db import Token, Contract


class TokenSubscriber(object):
    @staticmethod
    def handle_transfer(session, block, event, _from, to, value):
        token = session.query(Token).get(event.address)
        value = int(value)
        if _from == "0x0000000000000000000000000000000000000000":
            token.total_supply += value
            session.add(token)

        if to == "0x0000000000000000000000000000000000000000":
            token.total_supply -= value
            session.add(token)

