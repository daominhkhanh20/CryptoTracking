from abc import ABC
from src.db.mongodb import MongoClientConnector
from src.bot.telegram import TelegramBot
from src.utils.process import concurrent_process
from .base import BaseAnalysis
from collections import defaultdict
import prettytable
import locale
import logging

logger = logging.getLogger(__name__)


class VolumeAnalysis(BaseAnalysis, ABC):
    def __init__(self, bot: TelegramBot, mongodb: MongoClientConnector):
        self.bot = bot
        self.mongodb = mongodb
        self.list_tokens = self.mongodb.get_all_documents(database='information', collection='token')
        self.tokenomics = self.mongodb.get_all_documents(database='information', collection='tokenomic')
        self.list_token_ids = [token['id'] for token in self.list_tokens]
        self.mapping_id2name = {token['id']: token['name'] for token in self.list_tokens}
        self.mapping_id2symbol = {token['id']: token['symbol'] for token in self.list_tokens}
        self.data_table = []
        self.mapping_id2platform = defaultdict(list)
        for token in self.tokenomics:
            if token['contract_address'] is not None and len(token['contract_address']) > 0:
                id = token['id']
                for obj in token['contract_address']:
                    self.mapping_id2platform[id].append(obj['platform']['name'])

    def format_number(self, number):
        locale.setlocale(locale.LC_ALL, '')
        pretty_string = locale.format_string("%.2f", number, grouping=True)
        return pretty_string

    def convert_table(self, data_table):
        data_table = sorted(data_table, key=lambda x: x[-1], reverse=True)
        table = prettytable.PrettyTable(
            ['token_name', 'symbol', 'volume', 'market_cap', 'volume_market_cap_ratio', 'platform'])
        for data in data_table:
            table.add_row(data)
        return f'<pre>{table}</pre>'

    def analysis_crypto(self, token_id: str, date_str: str, dict_conditions: dict, **kwargs):
        query_result = self.mongodb.filter(database='price', collection=f"{token_id}_1D",
                                           dict_filter={"date_str": date_str})
        if len(query_result) == 1:
            query_result = query_result[0]
            volume = query_result['volume']
            market_cap = query_result['market_cap']
            data_infor = {
                # 'token_id': token_id,
                'token_name': self.mapping_id2name[token_id],
                'symbol': self.mapping_id2symbol[token_id],
                'volume': volume,
                'market_cap': market_cap,
                'volume_market_cap_ratio': volume / market_cap if market_cap != 0 else 0,
                'platform': self.mapping_id2platform[token_id]
            }
            for key, value in dict_conditions.items():
                if data_infor[key] < value:
                    return False
            for key in ['volume', 'market_cap', 'volume_market_cap_ratio']:
                data_infor[key] = self.format_number(data_infor[key])
            self.data_table.append(list(data_infor.values()))

    def analysis(self, channel_id: int, dict_conditions: dict, **kwargs):
        meta_data_documents = self.mongodb.get_all_documents(database='price', collection='price_metadata_1D')
        list_params = [(token['token_id'], token['max_date_str'], dict_conditions) for token in meta_data_documents]
        concurrent_process(self.analysis_crypto, list_params=list_params, num_workers=4)
        if len(self.data_table) > 0:
            logger.info(len(self.data_table))
            batch = kwargs.get('batch_send', 20)
            for idx, i in enumerate(range(0, len(self.data_table), batch)):
                data_table = self.data_table[i: min(i + batch, len(self.data_table))]
                text = self.convert_table(data_table)
                self.bot.send_message(channel_id=channel_id, text=f"Volume analysis table {idx}\n {text}",
                                      parse_mode='HTML')
