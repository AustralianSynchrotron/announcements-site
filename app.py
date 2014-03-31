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
Announcement = namedtuple('Announcement', 'name code group title recorded')
announcements = []
for code, (pv, value, group, title, recorded)  in codes.items():
    name = '{0}'.format(title)
    announcements.append(Announcement(name, code, group, title, recorded))

announced = None

class Root:
    @cherrypy.expose
    def index(self):
        global announced

        data = {}
        for announcement in announcements:
            group = announcement.group
            if group in data:
                data[group].append(announcement)
            else:
                data[group] = [ announcement ]
        return index.render(announcements=data,last_announcement=announced)

    @cherrypy.expose
    def announce(self, code):
        global announced

        code = int(code)
        print 'Announce request:', code
        try:
            pv = codes[code][0]
            value = codes[code][1]
            recorded = codes[code][4]
            print 'caput("{0}", "{1}")'.format(pv, value)
            caput(pv, value)
            success = True
            announced = recorded
        except KeyError:
            success = False
        return_data = {
                'success': success,
                'last_announcement': announced
        }
        return json.dumps(return_data)

cherrypy.config.update({'server.socket_port': 5560})
conf = {
       '/': {
           'tools.staticdir.on': True,
           'tools.staticdir.dir': os.path.join(current_dir, 'public')
       }
}

cherrypy.quickstart(Root(), script_name='/announcer', config=conf)
