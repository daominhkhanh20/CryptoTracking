import time
from datetime import datetime
from tqdm import tqdm
import sys
import logging
from collections import defaultdict
from src.processor.network import NetworkProcessor
from src.db.mongodb import MongoClientConnector
from src.utils.process import *
from src.utils.io import *
import random
logger = logging.getLogger(__name__)


class CrawlTokenomics:
    def __init__(self, mongodb: MongoClientConnector, list_header_keys: list, timeout: int = 100):
        self.mongodb = mongodb
        self.network = NetworkProcessor(timeout=timeout)
        self.crypto_category = defaultdict(list)
        self.list_header_keys = list_header_keys

    def get_categories(self):
        header = {
            'X-CMC_PRO_API_KEY': random.choice(self.list_header_keys),
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        all_crypto_categories = loop_request(
            network=self.network,
            url='https://pro-api.coinmarketcap.com/v1/cryptocurrency/categories',
            params={
                'limit': 5000
            },
            header=header,
            limit=5000
        )
        return all_crypto_categories

    def crawl_category(self, category_id: str, category_name: str):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/category'
        params = {
            'id': category_id,
            'limit': 1000,
            'start': 1
        }
        all_coins = []
        category_infor = None
        header = {
            'X-CMC_PRO_API_KEY': random.choice(self.list_header_keys),
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        while True:
            response = self.network.requests(url, params=params, headers=header)
            if response is None or 'data' not in response or len(response['data'].get('coins', [])) == 0:
                time.sleep(5)
                break
            all_coins.extend(response['data']['coins'])
            if category_infor is None:
                data = response['data']
                del data['coins']
                category_infor = data
            params['start'] += 1000
        if category_infor is not None:
            date_infor = category_infor['last_updated']
            for coin in all_coins:
                self.crypto_category[coin['id']].append({
                    'category_name': category_name,
                    'category_id': category_id
                })
            category_infor['coins'] = [token['id'] for token in all_coins]
            category_infor['partition'] = datetime.now().strftime('%Y%m%d')
            self.mongodb.insert_data(
                database='categories',
                collection_str=category_infor['title'],
                data=[category_infor]
            )
        else:
            print(response)
            print(category_id, category_name)

    def crawling_tokenomic(self, batch_token_ids: list):
        batch_token_ids = [str(token_id) for token_id in batch_token_ids]
        url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
        params = {
            'id': ','.join(batch_token_ids)
        }
        header = {
            'X-CMC_PRO_API_KEY': random.choice(self.list_header_keys),
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        response = self.network.requests(url=url, params=params, headers=header)
        if 'data' in response:
            data = response['data']
            list_filters, list_docs = [], []
            for id, token_info in data.items():
                list_filters.append({'id': token_info['id']})
                token_info['category'] = self.crypto_category.get(token_info['id'], None)
                del token_info['self_reported_circulating_supply']
                list_docs.append({'$set': token_info})
            self.mongodb.bulk_update_one(
                database='information',
                collection='tokenomic',
                list_filters=list_filters,
                list_docs=list_docs,
                batch_token_ids=batch_token_ids
            )
        else:
            logger.info(response)

    def crawling(self, **kwargs):
        # all_categories = self.get_categories()
        # logger.info(f"we have {len(all_categories)} categories")
        # list_params = [(cat['id'], cat['title']) for cat in all_categories]
        # # update category information by date
        # logger.info("Start crawling category information")
        # concurrent_process(self.crawl_category, list_params, num_workers=kwargs.get('max_workers', 3), time_sleep=0)
        all_tokens = self.mongodb.get_all_documents(database='information', collection='token')
        list_token_ids = [token['id'] for token in all_tokens]
        list_params = []
        logger.info("Start update tokenomic information")
        batch = kwargs.get('batch_size', 100)
        for i in range(0, len(all_tokens), batch):
            list_params.append([list_token_ids[i: min(i + batch, len(all_tokens))]])
        concurrent_process(self.crawling_tokenomic, list_params, num_workers=kwargs.get('max_workers', 2), time_sleep=0)
