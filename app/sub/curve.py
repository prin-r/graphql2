from app.db import Curve


class CurveSubscriber(object):
    def handle_curve_multiplier_change(
        session, block, event, previous_value, next_value
    ):
        curve = session.query(Curve).get(event.address)
        curve.curve_multiplier = next_value
        session.add(curve)
