def get_redis_connection():
    """Get redis connection instance."""
    pass


def get_redis_db(connection) -> dict:
    return connection.info("keyspace")
