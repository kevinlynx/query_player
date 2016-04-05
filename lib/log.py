# kevinlynx@gmail.com
import logging, os
from logging.handlers import RotatingFileHandler

LOG_HOME = 'log'
if not os.path.exists(LOG_HOME):
    os.makedirs(LOG_HOME)

logger = logging.getLogger('spm')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(LOG_HOME + '/spm.log', maxBytes = 1024 * 1024 * 100, backupCount = 10)
formatter = logging.Formatter('%(process)d %(asctime)s-%(name)s-%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
