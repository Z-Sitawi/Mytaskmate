#!/usr/bin/python3
""" Blueprint for API """
from flask import Blueprint

app_views = Blueprint('app_views', __name__)

from web_dynamic.api.v1.views.index import *
from web_dynamic.api.v1.views.users import *
from web_dynamic.api.v1.views.missions import *
from web_dynamic.api.v1.views.tasks import *
