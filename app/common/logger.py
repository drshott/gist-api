import logging
from logging import StreamHandler

def setup_logger():
    """ setup logger to log tasks """
    # set log handler properties
    handler = StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] - {%(pathname)s:%(lineno)d} - %(levelname)s - %(name)s::%(funcName)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    # set logger properties
    logger_name = 'gist-logger'
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

loghandle = setup_logger()
