from src.utils.io import load_yaml_file
from src.bot.telegram import TelegramBot
config = load_yaml_file('config/config.yml')
bot_token = config['environments']['telegram']['api_key']
channel_id = config['environments']['telegram']['channel_id']
bot = TelegramBot(bot_token=bot_token)
bot.send_message(channel_id=-1002076903202, text='   Name  Age        City\n  Alice   25    New York\n    Bob   30 Los Angeles\nCharlie   35     Chicago', parse_mode='HTML')