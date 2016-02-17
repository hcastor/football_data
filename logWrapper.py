import os
import logging
from datetime import datetime

def makeLogger(loggerName, logDir):
    if not os.path.isdir(logDir):
        os.mkdir(logDir)

    loggerName = str(loggerName)
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    timeStamp = datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
    debug_file_name = logDir + 'debug_' + loggerName + timeStamp + '.log'
    error_file_name = logDir + 'error_'+ loggerName + timeStamp +'.log'
    dfh = logging.FileHandler(debug_file_name)
    dfh.setLevel(logging.DEBUG)
    efh = logging.FileHandler(error_file_name)
    efh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s |~| %(processName)s |~| %(name)s |~| %(levelname)s |~| %(message)s')
    efh.setFormatter(formatter)
    dfh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(efh)
    logger.addHandler(dfh)
    return logger

def closeLogger(loggerName):
    loggerName = str(loggerName)
    logger = logging.getLogger(loggerName)
    handlers = logger.handlers[:]
    while len(handlers):
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)
        handlers = logger.handlers[:]