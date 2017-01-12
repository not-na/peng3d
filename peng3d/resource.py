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

try:
    import fastjson as json
except ImportError:
    import json
try:
    from .libs import jsoncomment as _jsoncomment
    json = _jsoncomment.JsonComment(json)
except ImportError:
    # try with a locally installed version, may not be fully compatible but worth a try
    try:
        import jsoncomment as _jsoncomment
        json = _jsoncomment.JsonComment(json)
    except ImportError:
        # not found at all, most features will still work, but comments and extraneous commas in JSON files will not
        pass

from . import model

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
        
        self.modelcache = {}
        
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
    def addFromTex(self,name,img,category):
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
    
    def getModelData(self,name):
        if name in self.modelcache:
            return self.modelcache[name]
        return self.loadModelData(name)
    def loadModelData(self,name):
        path = self.resourceNameToPath(name,".json")
        try:
            data = json.load(open(path,"r"))
        except Exception:
            self.od.exception("Exception during parsing of model %s"%name)
            return {}# will probably cause other exceptions later on, TODO
        
        out = {}
        
        if data.get("version",1)==1:
            # Currently only one version, basic future-proofing
            # This version should get incremented with breaking changes to the structure
            
            # Materials
            out["materials"]={}
            for name,matdata in data.get("materials",{}).items():
                m = model.Material(self,name,matdata)
                out["materials"][name]=m
            out["default_material"]=out["materials"][data.get("default_material",list(out["materials"].keys())[0])]
            
            # Bones
            out["bones"]={"__root__":model.RootBone(self,"__root__",{"start_rot":[0,0],"length":0})}
            for name,bonedata in data.get("bones",{}).items():
                b = model.Bone(self,name,bonedata)
                out["bones"][name]=b
            for name,bone in out["bones"].items():
                if name == "__root__":
                    continue
                bone.setParent(out["bones"][bone.bonedata["parent"]])
            
            # Regions
            out["regions"]={}
            for name,regdata in data.get("regions",{}).items():
                r = model.Region(self,name,regdata)
                r.material = out["materials"][regdata.get("material",out["default_material"])]
                r.bone = out["bones"][regdata.get("bone","__root__")]
                out["bones"][regdata.get("bone","__root__")].addRegion(r)
                out["regions"][name]=r
            
            # Animations
            out["animations"]={}
            out["animations"]["static"]=model.Animation(self,"static",{"type":"static","bones":{}})
            for name,anidata in data.get("animations",{}).items():
                a = model.Animation(self,name,anidata)
                a.setBones(out["bones"])
                out["animations"][name]=a
            out["default_animation"]=out["animations"][data.get("default_animation",out["animations"]["static"])]
        else:
            raise ValueError("Unknown version %s of model '%s'"%(data.get("version",1),name))
        
        self.modelcache[name]=out
        return out
