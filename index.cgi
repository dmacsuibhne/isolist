#!/usr/bin/python
import sys
sys.path.insert(0, '/home/donnchadh.macsuibhne/Desktop/isolist/isolist')

from wsgiref.handlers import CGIHandler
from isolist import app



CGIHandler().run(app)
