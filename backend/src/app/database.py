import sys

import structlog
from pymongo import IndexModel, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, DuplicateKeyError, OperationFailure

from app.core.config import get_settings

logger = structlog.get_logger().bind(context="database")


def get_mongo() -> MongoClient:
    """Initialize MongoDB client with connection verification."""
    settings = get_settings()
    try:
        client = MongoClient(
            settings.MONGO_CONNECTION_STRING,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )
        client.admin.command("ping")
        logger.info("MongoDB connection established")
        return client
    except ConnectionFailure as err:
        logger.error("MongoDB connection failed", error=repr(err))
        raise


def get_database() -> Database:
    settings = get_settings()
    return client.get_database(settings.MONGO_DB_NAME)


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


# Initialize client on module import
try:
    client = get_mongo()
except Exception:
    sys.exit(1)
