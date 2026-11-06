import json
import logging
from time import monotonic

from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


def consume_one_notification(
    consumer: KafkaConsumer, timeout_seconds: float = 15
) -> dict:
    """Прочитать и залогировать одно событие из подписанного топика."""
    if timeout_seconds <= 0:
        raise ValueError("Время ожидания должно быть положительным.")
    deadline = monotonic() + timeout_seconds
    while (remaining := deadline - monotonic()) > 0:
        batches = consumer.poll(
            timeout_ms=max(1, min(1000, int(remaining * 1000))), max_records=1
        )
        for records in batches.values():
            for record in records:
                event = json.loads(record.value.decode("utf-8"))
                if (
                    type(event.get("id")) is not int
                    or not isinstance(event.get("item_name"), str)
                ):
                    raise ValueError("Событие должно содержать id и item_name заказа.")
                logger.info(
                    "Получен заказ id=%s, item_name=%s",
                    event["id"], event["item_name"],
                )
                return event
    raise TimeoutError("Не получено событие о новом заказе.")
