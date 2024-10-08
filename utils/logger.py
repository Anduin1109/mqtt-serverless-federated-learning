import logging
import sys
sys.path.append('..')
import config


def get_logger(name, level=logging.INFO, color='black'):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        config.colors[color] +
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s' +
        config.colors['black']
    )
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
