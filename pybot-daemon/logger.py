import logging
import logging.handlers

def get_logger(name, logfile):
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)s %(name)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    file_handler.setLevel(logging.DEBUG)
    rotation_handler = logging.handlers.RotatingFileHandler(logfile, 
            maxBytes=20, backupCount=3)
    logger.debug("logger initialized %s" % logfile)
    return logger

def get_child_logger(logger, name, logfile):
    child_logger = logger.getChild(name)
    file_handler = logging.FileHandler(logfile)
    logger.addHandler(file_handler)
    logger.debug("child logger initialized %s" % logfile)
    return child_logger 

def shutdown():
    logging.shutdown()

