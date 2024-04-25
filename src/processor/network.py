import requests
import logging

logger = logging.getLogger(__name__)


class NetworkProcessor:
    def __init__(self, timeout: int = 100, **kwargs):
        self.timeout = timeout
        self.__dict__.update(kwargs)
        self.logger_error = []

    def requests(self, url: str, params=None, headers=None, method: str = 'get'):
        try:
            if method == 'get':
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            else:
                response = requests.post(url, params=params, headers=headers, timeout=self.timeout)
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger_error.append({
                "url": url,
                "params": params,
                "headers": headers
            })
            logger.error(str(e))
