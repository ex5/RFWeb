import logging
import logging.handlers

def get_logger(name, logfile):
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    rotation_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=10**9, backupCount=2)
    logger.addHandler(rotation_handler)
    logger.debug("logger initialized %s" % logfile)
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    return logger

def get_child_logger(logger, name, logfile):
    child_logger = logger.getChild(name)
    file_handler = logging.FileHandler(logfile)
    logger.addHandler(file_handler)
    logger.debug("child logger initialized %s" % logfile)
    return child_logger 

def shutdown():
    logging.shutdown()

