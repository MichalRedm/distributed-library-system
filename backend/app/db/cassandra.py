from cassandra.cluster import Cluster, Session
from typing import Optional
# from cassandra.auth import PlainTextAuthProvider


cluster: Optional[Cluster] = None
session: Optional[Session] = None


async def init_cassandra() -> None:
    global cluster, session
    # add more IPs for multiple nodes
    cluster = Cluster(['127.0.0.2', '127.0.0.3'])
    session = cluster.connect('data')
    print("Connected to Cassandra")


async def close_cassandra() -> None:
    if cluster:
        cluster.shutdown()
        print("Cassandra connection closed")


def get_session() -> Session:
    if session is None:
        raise RuntimeError(
            "Cassandra session is not initialized. "
            "Call init_cassandra() first."
        )
    return session
