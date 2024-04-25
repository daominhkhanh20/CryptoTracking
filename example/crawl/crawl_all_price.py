import argparse
from src.crawl.price_history import CrawlPriceHistory
from src.db.mongodb import MongoClientConnector
from src.utils.io import load_yaml_file
parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default='update')

args = parser.parse_args()

config = load_yaml_file('config/config.yml')
mongodb = MongoClientConnector(uri_mongo_connect=config['environments']['uri_mongodb_connect'])
crawling = CrawlPriceHistory(mongodb=mongodb,  list_header_keys=config['environments']['coin_marketcap_api_key'], timeout=100)
crawling.crawling(num_workers=2, time_sleep=1.5, mode=args.mode)