#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 20:37
# @Author  : 曾凌峰
# @Site    : 
# @File    : core.py
# @Software: PyCharm

import logging
import os
import base64
import errors

class Singleton(type):
    _instances = {}
    def __init__(cls, classname, parenttuple, attrdict):
        super(Singleton, cls).__init__(classname, parenttuple, attrdict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
            Singleton._instances[cls.__name__] = cls._instance
        return cls._instance


def get_logger(debug, loggername, file):
    logger = logging.getLogger(loggername)
    if debug:
        hdl = logging.StreamHandler()
        level = logging.DEBUG
    else:
        level = logging.INFO
        hdl = logging.FileHandler(file, mode='a')
        hdl.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    hdl.setFormatter(fmt)
    if not logger.handlers:
        logger.addHandler(hdl)
    logger.setLevel(level) # change to DEBUG for higher verbosity
    return logger


def load_picture(path, filename, image_base64):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        imgfile = base64.b64decode(image_base64)
    except:
        raise RuntimeError(errors.PORTRAIT_SHOULD_BE_BASE64)
    pathname = os.path.join(path, filename)
    with open(pathname, 'wb') as f:
        f.write(imgfile)
    return pathname


def path_to_url(datapath, path):
    if datapath in path:
        return path.replace(datapath, '/data')


#由于给redis传None,返回会得到'None'，不便于处理
def validhash(datadict):
    rs = {}
    if not isinstance(datadict, dict):
        return
    for key, value in datadict.iteritems():
        if value:
            rs[key] = value
    return rs