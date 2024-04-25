from typing import *
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo import UpdateOne
from pandas import DataFrame
from typing import List
import logging

logger = logging.getLogger(__name__)


class MongoClientConnector:
    def __init__(self, uri_mongo_connect: str):
        self.uri_mongo_connect = uri_mongo_connect
        self.mongo_client = MongoClient(self.uri_mongo_connect)

    def insert_data(self, database: str, collection_str: str, data: List[dict]):
        collection = self.mongo_client[database][collection_str]
        collection.insert_many(data)
        logger.info(f"Insert to {database}/{collection_str} with {len(data)} records")

    def filter(self, database: str, collection: str, dict_filter:dict):
        collection = self.mongo_client[database][collection]
        query_result = collection.find(dict_filter)
        return list(query_result)

    def get_all_documents(self, database: str, collection: str):
        return list(self.mongo_client[database][collection].find({}))

    def collection_update_one(self, database, collection, filter: dict, doc: dict):
        self.mongo_client[database][collection].replace_one(
            filter=filter,
            replacement=doc,
            upsert=True
        )

    def bulk_update_one(self, database: str, collection: str, list_filters: list, list_docs, **kwargs):
        try:
            requests = [UpdateOne(filter=filter_doc, update=doc, upsert=True) for filter_doc, doc in zip(list_filters, list_docs)]
            self.mongo_client[database][collection].bulk_write(requests)
        except Exception as e:
            logger.error(str(e))
            logger.info(list_filters)
            logger.info(list_docs)
            logger.info(f"{kwargs.get('batch_token_ids')}")

