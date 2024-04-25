from datetime import datetime
from tqdm import tqdm
import sys
import random
from dateutil import parser
from src.processor.network import NetworkProcessor
from src.db.mongodb import MongoClientConnector
from src.utils.process import *
from src.utils.io import *


class CrawlPriceHistory:
    def __init__(self, mongodb: MongoClientConnector, list_header_keys: list, timeout: int = 5):
        self.mongodb = mongodb
        self.network = NetworkProcessor(timeout=timeout)
        self.list_header_keys = list_header_keys
        self.list_tokens = self.mongodb.get_all_documents(database='information', collection='token')
        self.list_token_ids = [token['id'] for token in self.list_tokens]
        self.mapping_id2name = {token['id']: token['name'] for token in self.list_tokens}
        self.mapping_id2symbol = {token['id']: token['symbol'] for token in self.list_tokens}

    def crawling_price_1d_all(self, token_id: int, range: str, **kwargs):
        url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart"
        params = {
            'id': token_id,
            "range": '1Y'
        }
        headers = {
            'X-CMC_PRO_API_KEY': random.choice(self.list_header_keys),
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        response = self.network.requests(url, params=params, headers=headers)
        current_market_cap = 0
        current_volume = 0
        current_circulating_supply = 0

        min_date = kwargs.get('min_date', None)
        if response is not None and len(response['data'].get('points', {})) > 0:
            data = response['data']['points']
            data_insert = []
            max_date = list(data.keys())[0]
            for key, value in data.items():
                if min_date is not None and datetime.fromtimestamp(int(key)).strftime('%Y%m%d') < min_date:
                    continue

                if key > max_date:
                    max_date = key
                    current_market_cap = value['v'][2]
                    current_volume = value['v'][1]
                    current_circulating_supply = value['v'][4]
                time_normal = datetime.fromtimestamp(int(key)).strftime('%Y%m%d')
                result = {
                    "price": value['v'][0],
                    'volume': value['v'][1],
                    'market_cap': value['v'][2],
                    'circulating_supply':  value['v'][4],
                    'date_timestamp': key,
                    'date_str': time_normal,
                    'token_id': token_id,
                    'token_name': self.mapping_id2name[token_id],
                    'symbol': self.mapping_id2symbol[token_id]
                }
                data_insert.append(result)
            self.mongodb.insert_data(database='price', collection_str=f"{token_id}_{range}",
                                     data=data_insert)
            self.mongodb.insert_data(
                database='price', collection_str=f'price_metadata_{range}', data=[
                    {
                        'token_id': token_id,
                        'token_name': self.mapping_id2name[token_id],
                        'symbol': self.mapping_id2symbol[token_id],
                        'max_date': max_date,
                        'max_date_str': datetime.fromtimestamp(int(max_date)).strftime('%Y%m%d'),
                        'current_market_cap': current_market_cap,
                        "current_volume": current_volume,
                        'current_circulating_supply': current_circulating_supply
                    }
                ]
            )

    def update_price_1d(self, data_raw: dict):
        meta_data = self.mongodb.filter(
            database='price',
            collection='price_metadata_1D',
            dict_filter={'token_id': data_raw['id']}
        )
        temp = data_raw['quote']['USD']
        data = {
            'price': temp['price'],
            'volume': temp['volume_24h'],
            'market_cap': temp['market_cap'],
            'fully_diluted_market_cap': temp['fully_diluted_market_cap'],
            'date_timestamp': int(parser.parse(temp['last_updated']).timestamp()),
            'date_str': datetime.fromtimestamp(int(parser.parse(temp['last_updated']).timestamp())).strftime('%Y%m%d'),
            "token_id": data_raw['id'],
            'circulating_supply': data_raw['circulating_supply'],
            'total_supply': data_raw['total_supply'],
            'symbol': self.mapping_id2symbol[data_raw['id']],
            'token_name': self.mapping_id2name[data_raw['id']],
        }
        current_date = datetime.strptime(data['date_str'], '%Y%m%d')
        if len(meta_data) == 0:
            self.crawling_price_1d_all(token_id=data['token_id'], range='1D')
        elif len(meta_data) > 1:
            logger.error("Duplicate token id")
        else:
            meta_data = meta_data[0]
            last_date = datetime.strptime(meta_data['max_date_str'], '%Y%m%d')
            delta_day = (current_date - last_date).days
            if delta_day == 1:
                self.mongodb.insert_data(database='price', collection_str=f"{data_raw['id']}_1D", data=[data])
                meta_data['max_date'] = int(current_date.timestamp())
                meta_data['max_date_str'] = current_date.strftime('%Y%m%d')
                self.mongodb.collection_update_one(
                    database='price',
                    collection='price_metadata_1D',
                    filter={'token_id': data['token_id']},
                    doc=meta_data
                )
            elif delta_day == 0:
                logger.info(f"{data_raw['id']} nothing happen")
            elif delta_day > 1:
                self.crawling_price_1d_all(
                    token_id=data['token_id'],
                    min_date=data['date_str'],
                    range='1D'
                )

    def update_data(self, **kwargs):
        headers = {
            'X-CMC_PRO_API_KEY': random.choice(self.list_header_keys),
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        params = {
            "limit": 5000,
            "start": 1
        }
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        data = []
        while True:
            response = self.network.requests(url, params=params, headers=headers)
            if 'data' not in response or len(response['data']) == 0:
                break
            params['start'] += 5000
            data.extend(response['data'])
        list_params = [[sample] for sample in data]
        concurrent_process(func=self.update_price_1d, list_params=list_params, num_workers=kwargs.get('num_workers', 2))

    def crawling(self, num_workers: int = 2, mode: str = 'all', **kwargs):
        list_params = []
        if mode == 'all':
            for range_time in ['1D']:
                for token_id in self.list_token_ids:
                    list_params.append((token_id, range_time))
            logger.info(f"Start crawling {len(list_params)}")
            concurrent_process(self.crawling_price_1d_all, list_params=list_params, num_workers=num_workers, time_sleep=kwargs.get('time_sleep', 1))
        elif mode == 'update':
            self.update_data()
        write_json(self.network.logger_error, 'data/log_error.json')
