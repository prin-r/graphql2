from app.db import TokenLocked, Balance
from sqlalchemy import func


def get_max_lock(session, token_address, user):
    return (
        session.query(func.max(TokenLocked.value))
        .filter_by(token_address=token_address, user=user)
        .scalar()
        or 0
    )


class TokenLockedSubscriber(object):
    @staticmethod
    def handle_token_locked(session, block, event, locker, owner, value):
        token_locked = session.query(TokenLocked).get(
            (event.address, locker, owner)
        )
        if token_locked is None:
            session.add(
                TokenLocked(
                    token_address=event.address,
                    locker=locker,
                    user=owner,
                    value=value,
                )
            )
        else:
            token_locked.value += value
            session.add(token_locked)

        balance = session.query(Balance).get((event.address, owner))
        balance.locked_value = get_max_lock(session, event.address, owner)
        session.add(balance)

    @staticmethod
    def handle_token_unlocked(session, block, event, locker, owner, value):
        token_locked = session.query(TokenLocked).get(
            (event.address, locker, owner)
        )
        if token_locked.value == value:
            session.delete(token_locked)
        else:
            token_locked.value -= value
            session.add(token_locked)

        balance = session.query(Balance).get((event.address, owner))
        balance.locked_value = get_max_lock(session, event.address, owner)
        session.add(balance)
