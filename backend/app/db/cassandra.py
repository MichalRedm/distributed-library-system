from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

cluster = None
session = None

async def init_cassandra():
    global cluster, session
    cluster = Cluster(['127.0.0.2', '127.0.0.3'])  # add more IPs for multiple nodes
    session = cluster.connect('data')
    print("Connected to Cassandra")

async def close_cassandra():
    if cluster:
        cluster.shutdown()
        print("Cassandra connection closed")

def get_session():
    return session
