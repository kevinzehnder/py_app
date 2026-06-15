import structlog
from pymongo import IndexModel, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, OperationFailure

from app.core.config import get_settings

logger = structlog.get_logger().bind(context="database")

# Lazily-constructed singleton. MongoClient() does no network I/O on
# construction — only ensure_connection() and real queries hit the server.
_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return the lazily-constructed MongoDB client."""
    if not get_settings().MONGO_ENABLED:
        raise RuntimeError("MongoDB is disabled (set MONGO_ENABLED=true to use it)")
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(
            settings.MONGO_CONNECTION_STRING,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )
    return _client


def ensure_connection() -> None:
    """Ping the server to validate connectivity; raises on failure.

    Call from the app lifespan startup so misconfiguration fails loudly.
    """
    get_client().admin.command("ping")
    logger.info("MongoDB connection established")


def get_database() -> Database:
    return get_client().get_database(get_settings().MONGO_DB_NAME)


def get_collection(collection_name: str) -> Collection:
    return get_database().get_collection(collection_name)


def create_collection_indices() -> None:
    """Create indices for all collections. Extend for each new resource."""
    indices: dict[str, list[IndexModel]] = {
        "items": [
            IndexModel("name"),
            IndexModel("active"),
        ],
    }

    for collection_name, index_list in indices.items():
        collection = get_collection(collection_name)
        try:
            collection.create_indexes(index_list)
            logger.info("created indices", collection=collection_name)
        except DuplicateKeyError as e:
            logger.debug("index already exists", collection=collection_name, error=repr(e))
        except OperationFailure as e:
            logger.error("failed to create indices", collection=collection_name, error=repr(e))
            raise


def close_client() -> None:
    """Close the MongoDB client. Call from app lifespan shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")
