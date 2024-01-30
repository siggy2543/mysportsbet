import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def log_error(error_message):
    logger.error(error_message)

def log_info(info_message):
    logger.info(info_message)


# Python's logging module can be used for logging important events and errors.