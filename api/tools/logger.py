import logging
import os


def setup_logger(log_level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    file_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "api_debug.log"))
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
