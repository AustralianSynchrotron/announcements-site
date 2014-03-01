#!/usr/bin/env python
import cherrypy
import json
from jinja2 import Environment, FileSystemLoader
import os
from collections import namedtuple
from codes import codes
from epics import caput

current_dir = os.path.dirname(os.path.abspath(__file__))

loader = FileSystemLoader(os.path.join(current_dir, 'templates'))
env = Environment(loader=loader)
index = env.get_template('index.html')
Announcement = namedtuple('Announcement', 'name code')
announcements = []
for code, (pv, value)  in codes.items():
    name = '{0} = {1}'.format(pv, value)
    announcements.append(Announcement(name, code))

class Root:
    @cherrypy.expose
    def index(self):
        return index.render(announcements=announcements)

    @cherrypy.expose
    def announce(self, code):
        code = int(code)
        print 'Announce request:', code
        try:
            pv, value = codes[code] 
            print 'caput({0}, {1})'.format(pv, value)
            caput(pv, value)
            success = True
        except KeyError:
            success = False
        return_data = {
                'success': success
        }
        return json.dumps(return_data)

cherrypy.config.update({'server.socket_port': 5560})
conf = {
       '/': {
           'tools.staticdir.on': True,
           'tools.staticdir.dir': os.path.join(current_dir, 'bootstrap')
       }
}

cherrypy.quickstart(Root(), script_name='/announcer', config=conf)
