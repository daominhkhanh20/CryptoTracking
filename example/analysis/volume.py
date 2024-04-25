from src.utils.io import load_yaml_file
from src.bot.telegram import TelegramBot
from src.analysis.volume import VolumeAnalysis
from src.db.mongodb import MongoClientConnector
config = load_yaml_file('config/config.yml')
bot_token = config['environments']['telegram']['api_key']
channel_id = config['environments']['telegram']['channel_id']
bot = TelegramBot(bot_token=bot_token)
mongodb = MongoClientConnector(uri_mongo_connect=config['environments']['uri_mongodb_connect'])
volume_analysis = VolumeAnalysis(
    mongodb=mongodb,
    bot=bot
)
dict_conditions = config['analysis']['volume_analysis']
volume_analysis.analysis(channel_id=channel_id, dict_conditions=dict_conditions, batch_send=10)