# -*- coding:utf-8 -*-

import os, time
import logging
import logging.handlers
from functools import wraps


def init_log(log_path, logger=None, level=logging.INFO, when="D", backup=7,
             format="[%(levelname)s %(asctime)s %(filename)s:%(lineno)d] - {PID:%(process)d Thread:%(thread)d} *** %(message)s"):
    """
    init_log - initialize log module

    Args:
      log_path      - Log file path prefix.
                      Log data will go to two files: log_path.log and log_path.log.wf
                      Any non-exist parent directories will be created automatically
      logger        - default using logging.getLogger()
      level         - msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
                      the default value is logging.INFO
      when          - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
                      default value: 'D'
      format        - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
      backup        - how many backup file to keep
                      default value: 7

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    formatter = logging.Formatter(format)
    if not logger:
        logger = logging.getLogger()
    logger.setLevel(level)

    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup,
                                                        encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.wf",
                                                        when=when,
                                                        backupCount=backup,
                                                        encoding='utf-8')
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def logging_elapsed_time(func_desc):
    def func_wrapper(func):
        @wraps(func)
        def return_wrapper(*args, **wkargs):
            _startTime = time.time()
            rslt = func(*args, **wkargs)
            _endTime = time.time()
            logging.info('#####################################################################')
            logging.info(func_desc + ' --- Elapsed Time : ' + str(round(_endTime - _startTime, 2)) + 's')
            logging.info('#####################################################################')
            return rslt

        return return_wrapper

    return func_wrapper
