import logging


def init_logging() -> logging.Logger:
    log_format = '%(asctime)s %(threadName)+8s %(levelname)+8s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    return logger
