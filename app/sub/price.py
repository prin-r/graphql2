from decimal import Decimal
from sqlalchemy import func

from app.db import Price, Curve
from app.utils.equation import calculate_price_at


class PriceSubscriber(object):
    @staticmethod
    def handle_buy(
        session,
        block,
        event,
        buyer,
        bonded_token_amount,
        collateral_token_amount,
    ):
        PriceSubscriber.add_price(session, event.address, block.time)

    @staticmethod
    def handle_sell(
        session,
        block,
        event,
        seller,
        bonded_token_amount,
        collateral_token_amount,
    ):
        PriceSubscriber.add_price(session, event.address, block.time)

    @staticmethod
    def add_price(session, curve_address, timestamp):
        curve = session.query(Curve).get(curve_address)
        price = session.query(Price).get((curve_address, timestamp))
        value = PriceSubscriber.calculate_price(session, curve)

        if price is None:
            price = Price(
                curve_address=curve_address,
                price=value,
                timestamp=timestamp,
                total_supply=curve.token.total_supply,
            )
        else:
            price.price = value
        session.add(price)

        # Update price to curve
        curve = session.query(Curve).get(curve_address)
        curve.price = value
        session.add(curve)

    @staticmethod
    def calculate_price(session, curve):
        return (
            calculate_price_at(
                curve.collateral_equation, curve.token.total_supply
            )
            * curve.curve_multiplier
            / Decimal(10 ** 18)
        )
