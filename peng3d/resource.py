#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  resource.py
#  
#  Copyright 2016 notna <notna@apparat.org>
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

import os

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # Probably headless

class ResourceManager(object):
    def __init__(self,peng,basepath):
        self.basepath = basepath
        self.peng = peng
        maxsize = GLint()
        glGetIntegerv(GL_MAX_TEXTURE_SIZE,maxsize)
        maxsize = min(maxsize.value,self.peng.cfg["rsrc.maxtexsize"]) # This is here to avoid massive memory overhead when only loading a few textures
        self.texsize = maxsize
        self.categories = {}
        self.categoriesTexCache = {}
        self.categoriesTexBin = {}
        self.missingTexture = None
    def resourceNameToPath(self,name,ext=""):
        nsplit = name.split(":")[1].split(".")
        return os.path.join(self.basepath,"assets",name.split(":")[0],*nsplit)+ext
    def resourceExists(self,name,ext=""):
        return os.path.exists(self.resourceNameToPath(name,ext))
    def addCategory(self,name):
        self.categories[name]={}
        self.categoriesTexCache[name]={}
        self.categoriesTexBin[name]=pyglet.image.atlas.TextureBin(self.texsize,self.texsize)
    def getTex(self,name,category):
        if name not in self.categoriesTexCache[category]:
            self.loadTex(name,category)
        return self.categoriesTexCache[category][name]
    def loadTex(self,name,category):
        try:
            img = pyglet.image.load(self.resourceNameToPath(name,".png"))
        except FileNotFoundError:
            img = self.getMissingTexture()
        texreg = self.categoriesTexBin[category].add(img)
        #texreg = texreg.get_transform(True,True) # Mirrors the image due to how pyglets coordinate system works
        # Strange behaviour, sometimes needed and sometimes not
        self.categories[category][name]=texreg
        target = texreg.target
        texid = texreg.id
        texcoords = texreg.tex_coords
        # Prevents texture bleeding with texture sizes that are powers of 2, else weird lines may appear at certain angles.
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        out = target,texid,texcoords
        self.categoriesTexCache[category][name]=out
        return out
    def getMissingTexture(self):
        if self.missingTexture is None:
            if self.resourceExists("peng3d:missingtexture",".png"):
                self.missingTexture = pyglet.image.load(self.resourceNameToPath("peng3d:missingtexture",".png"))
                return self.missingTexture
            else: # Falls back to create pattern in-memory
                self.missingTexture = pyglet.image.create(1,1,pyglet.image.SolidColorImagePattern([255,0,255,255]))
                return self.missingTexture
        else:
            return self.missingTexture
    
