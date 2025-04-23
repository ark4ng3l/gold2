import logging
from datetime import datetime

def setup_logger():
    logging.basicConfig(
        filename='logs/system.log',
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

# در main.py فراخوانی شود