from src.processor.network import NetworkProcessor
from src.db.mongodb import MongoClientConnector
from src.crawl.tokenomics import CrawlTokenomics
from src.utils.io import load_yaml_file

config = load_yaml_file('config/config.yml')
network = NetworkProcessor(timeout=100)
mongodb = MongoClientConnector(uri_mongo_connect=config['environments']['uri_mongodb_connect'])

crawling = CrawlTokenomics(mongodb=mongodb, list_header_keys=config['environments']['coin_marketcap_api_key'])
crawling.crawling()
