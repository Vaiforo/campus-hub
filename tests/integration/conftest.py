from uuid import uuid4

import pytest
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.community.kafka import KafkaContainer
from testcontainers.community.postgres import PostgresContainer

from campushub.models import Base


@pytest.fixture
def session_factory():
    with PostgresContainer("postgres:16.6-alpine", driver="psycopg") as postgres:
        engine = create_engine(postgres.get_connection_url())
        try:
            Base.metadata.create_all(engine)
            yield sessionmaker(engine)
        finally:
            engine.dispose()


@pytest.fixture
def kafka_connection():
    with KafkaContainer("confluentinc/cp-kafka:7.6.0").with_kraft() as kafka:
        yield kafka.get_bootstrap_server()


@pytest.fixture
def order_topic(kafka_connection):
    topic = f"orders.created.{uuid4().hex}"
    admin = KafkaAdminClient(bootstrap_servers=kafka_connection)
    try:
        admin.create_topics([
            NewTopic(topic, num_partitions=1, replication_factor=1)
        ])
        yield topic
    finally:
        admin.close()


@pytest.fixture
def producer(kafka_connection, order_topic):
    producer = KafkaProducer(
        bootstrap_servers=kafka_connection,
        acks="all",
        max_block_ms=10000,
        request_timeout_ms=10000,
    )
    try:
        yield producer
    finally:
        producer.close(timeout=10)


@pytest.fixture
def consumer(kafka_connection, order_topic):
    consumer = KafkaConsumer(
        order_topic,
        bootstrap_servers=kafka_connection,
        group_id=f"notifications-{uuid4().hex}",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    try:
        yield consumer
    finally:
        consumer.close()
