#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  peng3d_ext.py
#  
#  Copyright 2017 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from sphinxcontrib.domaintools import custom_domain
import sphinxcontrib.domaintools

def get_objects(self):
        for (type, name), info in self.data['objects'].items():
            yield (name, name, type, info[0], info[1],
                   self.object_types[type].attrs['searchprio'])
sphinxcontrib.domaintools.CustomDomain.get_objects = get_objects

def setup(app):
    app.add_domain(custom_domain('peng3dDomain',
        name  = 'peng3d',
        label = "Peng3d",

        elements = dict(
            event  = dict(
                objname = "peng3d Event",
                indextemplate = "pair: %s; peng3d Event",
            ),
            pgevent  = dict(
                objname = "peng3d Pyglet Event",
                indextemplate = "pair: %s; peng3d Pyglet Event",
            ),
        )))
    return {"version":"1.0"}
