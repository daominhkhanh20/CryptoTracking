import time
import requests
import logging

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, bot_token: str):
        self.token = bot_token

    def send_message(self, channel_id: int, text: str, **kwargs):
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            params = {
                "chat_id": channel_id,
                "text": text,
            }
            params.update(**kwargs)
            response = requests.post(url, params=params)
        except Exception as e:
            logger.error(str(e))
