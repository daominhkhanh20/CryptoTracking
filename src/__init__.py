import logging
import sys
import warnings
import os
import colorlog

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)

formatted = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(log_color)s%(levelname)s:%(reset)s %(log_color)s%(name)s:%(reset)s%(lineno)d - %(log_color)s%(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

stream_handler.setFormatter(formatted)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
logger.propagate = False


__author__ = 'khanhdm'
__version__ = '0.1.1'