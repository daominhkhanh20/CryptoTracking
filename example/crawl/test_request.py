from src.processor.network import NetworkProcessor
from src.utils.io import write_json
network = NetworkProcessor(timeout=10)

data = []

params = {
    "id": 29814,
    "range": "1Y"
}
url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart"
response = network.requests(url=url, params=params, method='get')
print(len(response['data']['points']))
