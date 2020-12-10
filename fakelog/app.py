import logging.handlers
from time import sleep
import logging
import string
from loguru import logger


flag = True


while flag:
    try:
        logger.add(
            logging.handlers.SysLogHandler(address=('rsyslog', 10514))
        )
        flag = False
        logger.error('conectado ao rsyslog')
    except:
        logging.error('erro ao conectar com o rsyslog')
        sleep(1)

while True:
    for event in [f'log {k}' for k in string.ascii_uppercase]:        
        try:
            logger.info(event)
        except:
            logger.error('erro ao conectar com o rsyslog')
            pass

        sleep(1)
