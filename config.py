# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 15:53:03 2017

@author: seb
"""
# config.py

class Config(object):
    """
    Common configurations
    """

    DEBUG = True

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}