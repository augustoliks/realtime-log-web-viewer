import logging.handlers
from time import sleep
import logging
import string


my_logger = logging.getLogger()
my_logger.setLevel(logging.INFO)

flag = True


while flag:
    try:
        handler = logging.handlers.SysLogHandler(address=('rsyslog', 10514))
        my_logger.addHandler(handler)
        flag = False
    except:
        logging.error('erro ao conectar com o rsyslog')
        sleep(1)

logging.error('conectado ao rsyslog')

while True:
    for event in [f'log {k}' for k in string.ascii_uppercase]:        
        try:
            logging.info(event)
            print(event)
        except:
            logging.error('erro ao conectar com o rsyslog')
            pass

        sleep(1)
