import logging

import pytest
from sqlalchemy import func, select

from campushub.models import Order
from campushub.notifications import consume_one_notification
from campushub.orders import create_order
from tests.factories import OrderFactory

pytestmark = pytest.mark.integration


def test_saved_order_is_delivered_to_notifications(
    session_factory, producer, consumer, order_topic, caplog
):
    with session_factory() as session:
        session.add_all(OrderFactory.build_batch(3))
        session.commit()
        initial_count = session.scalar(select(func.count()).select_from(Order))

    order = OrderFactory.build()
    expected_name, expected_quantity = order.item_name, order.quantity
    assert order.id is None

    with session_factory() as session:
        created = create_order(order, session, producer, order_topic)
        order_id = created.id
        assert type(order_id) is int

    with session_factory() as session:
        saved = session.get(Order, order_id)
        assert saved is not None
        assert saved.item_name == expected_name
        assert saved.quantity == expected_quantity
        assert session.scalar(select(func.count()).select_from(Order)) == initial_count + 1

    with caplog.at_level(logging.INFO, logger="campushub.notifications"):
        event = consume_one_notification(consumer)

    assert event["id"] == order_id
    assert event["item_name"] == expected_name
    records = [
        record for record in caplog.records
        if record.name == "campushub.notifications"
    ]
    assert len(records) == 1
    assert records[0].args == (order_id, expected_name)
