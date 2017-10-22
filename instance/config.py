# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 15:59:09 2017

@author: seb
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_TRACK_MODIFICATIONS = 'False'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'p9Bv<3Eid9%$i01'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

