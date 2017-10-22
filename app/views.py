# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 15:59:09 2017

@author: seb
"""
# views.py

from flask import render_template

from app import app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")