from enums import QtAPI
from fields import *
from forms import *

__author__ = 'Juan Manuel Bermúdez Cabrera'

API = property(QtAPI.get_current, QtAPI.set_current)
