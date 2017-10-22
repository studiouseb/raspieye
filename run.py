# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 15:55:03 2017

@author: seb
"""
# run.py
import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', threaded=True,)
