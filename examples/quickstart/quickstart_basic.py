#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  quickstart_basic.py
#  
#  Copyright 2022 notna <notna@apparat.org>
#  
#  This file is part of peng3d.
#
#  peng3d is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  peng3d is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with peng3d.  If not, see <http://www.gnu.org/licenses/>.
#

import peng3d

peng = peng3d.Peng()

peng.createWindow(caption="Hello World!", resizable=True)

main_menu = peng3d.Menu("main", peng.window, peng)
peng.window.addMenu(main_menu)

peng.window.changeMenu("main")
peng.run()
