import io
import tarfile
from uuid import uuid4

import pytest
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

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
    # Start the broker after Docker assigns the external port so Kafka can
    # advertise the address reachable by clients outside its container.
    container = (
        DockerContainer("apache/kafka:3.9.1")
        .with_exposed_ports(9092)
        .with_env("KAFKA_NODE_ID", "1")
        .with_env("KAFKA_PROCESS_ROLES", "broker,controller")
        .with_env("KAFKA_LISTENERS", "PLAINTEXT://:9092,CONTROLLER://:9093")
        .with_env(
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP",
            "PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT",
        )
        .with_env("KAFKA_CONTROLLER_LISTENER_NAMES", "CONTROLLER")
        .with_env("KAFKA_CONTROLLER_QUORUM_VOTERS", "1@localhost:9093")
        .with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
        .with_env("KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", "1")
        .with_env("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "1")
        .with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")
        .with_kwargs(entrypoint=["/bin/sh", "-c"])
        .with_command([
            "while [ ! -f /tmp/start-kafka.sh ]; do sleep 0.1; done; "
            "exec /bin/bash /tmp/start-kafka.sh"
        ])
    )
    with container as kafka:
        address = f"{kafka.get_container_host_ip()}:{kafka.get_exposed_port(9092)}"
        script = (
            f"export KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://{address}\n"
            "exec /etc/kafka/docker/run\n"
        ).encode()
        with io.BytesIO() as archive:
            with tarfile.open(fileobj=archive, mode="w") as tar:
                info = tarfile.TarInfo("start-kafka.sh")
                info.size = len(script)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(script))
            kafka.get_wrapped_container().put_archive("/tmp", archive.getvalue())
        LogMessageWaitStrategy("Kafka Server started").with_startup_timeout(
            60
        ).wait_until_ready(kafka)
        yield address


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
