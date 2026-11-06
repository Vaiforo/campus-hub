import json

from kafka import KafkaProducer
from sqlalchemy.orm import Session

from campushub.models import Order


def create_order(
    order: Order,
    session: Session,
    producer: KafkaProducer,
    topic: str,
    timeout_seconds: float = 10,
) -> Order:
    """Сохранить заказ и дождаться подтверждения публикации события.

    Ошибка Kafka передаётся вызывающему коду; сохранённый заказ остаётся в БД.
    Сессия должна принадлежать только текущей операции.
    """
    try:
        session.add(order)
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(order)
    event = {"id": order.id, "item_name": order.item_name}
    producer.send(
        topic, value=json.dumps(event, ensure_ascii=False).encode("utf-8")
    ).get(timeout=timeout_seconds)
    return order
