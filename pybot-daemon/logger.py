import logging
import logging.handlers

def get_logger(logfile, name=None):
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger()
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name) %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    rotation_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=5*10**6, backupCount=3)
    logger.addHandler(rotation_handler)
    logger.setLevel(logging.DEBUG)
    logger.debug("logger initialized %s" % logfile)
    return logger

def shutdown():
    logging.shutdown()

