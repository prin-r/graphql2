from app.db import Order


class OrderSubscriber(object):
    @staticmethod
    def handle_buy(
        session,
        block,
        event,
        buyer,
        bonded_token_amount,
        collateral_token_amount,
    ):
        OrderSubscriber.add_order(
            session,
            block,
            event,
            "Buy",
            buyer,
            bonded_token_amount,
            collateral_token_amount,
        )

    @staticmethod
    def handle_sell(
        session,
        block,
        event,
        seller,
        bonded_token_amount,
        collateral_token_amount,
    ):
        OrderSubscriber.add_order(
            session,
            block,
            event,
            "Sell",
            seller,
            bonded_token_amount,
            collateral_token_amount,
        )

    @staticmethod
    def add_order(session, block, event, order_type, user, amount, price):
        session.add(
            Order(
                curve_address=event.address,
                block_height=block.height,
                log_index=event.log_index,
                order_type=order_type,
                user=user,
                amount=amount,
                price=price,
                timestamp=block.time,
                tx_hash=event.tx_hash,
            )
        )
