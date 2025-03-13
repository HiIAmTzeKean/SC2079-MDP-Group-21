import logging


log_format = logging.Formatter("%(asctime)s :: %(levelname)s :: %(processName)s :: %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = True

if not logger.hasHandlers():
    # Console handler
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_format)

    # File handler
    txt_handler = logging.FileHandler("logfile.txt")
    txt_handler.setLevel(logging.DEBUG)
    txt_handler.setFormatter(log_format)

    # Add handlers to logger
    logger.addHandler(debug_handler)
    logger.addHandler(txt_handler)

logger.info("started package")