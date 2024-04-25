from src.processor.network import NetworkProcessor
from src.db.mongodb import MongoClientConnector
from src.utils.io import load_yaml_file
import random
network = NetworkProcessor(timeout=100)
config = load_yaml_file('config/config.yml')
list_headers = config['environments']['coin_marketcap_api_key']
mongodb = MongoClientConnector(uri_mongo_connect=config['environments']['uri_mongodb_connect'])
headers = {
  'X-CMC_PRO_API_KEY': random.choice(list_headers),
  'Accept': 'application/json',
  'Accept-Encoding': 'deflate, gzip'
}
params = {
    "listing_status": "active",
    "limit": 5000
}
list_filters, list_docs = [], []
url = "https://pro-api.coinmarketcap.com/v1/exchange/map"
start = 1
while True:
    params['start'] = start
    response = network.requests(url=url, params=params, headers=headers, method='get')
    if len(response['data']) == 0:
        break
    for doc in response['data']:
        list_docs.append({'$set': doc})
        list_filters.append({'id': doc['id']})
    start += 5000
print(f"Update {len(list_docs)} exchanges")
mongodb.bulk_update_one(database='information', collection='exchange', list_docs=list_docs, list_filters=list_filters)

