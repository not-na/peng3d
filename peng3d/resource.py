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

__all__ = ["ResourceManager"]

import os

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass  # Probably headless

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
    """
    Manager that allows for efficient and simple loading and management of different kinds of resources.
    
    Currently supports textures and models out of the box, but extension is possible.
    
    Textures can be queried by any part of the application, they are only loaded on the first request and then cached for every request following it.
    
    The same caching and lazy-loading principle applies to models loaded via this system.
    """
    missingtexturename = "peng3d:missingtexture"
    def __init__(self,peng,basepath):
        self.basepath = basepath
        self.peng = peng
        
        maxsize = GLint()
        glGetIntegerv(GL_MAX_TEXTURE_SIZE,maxsize)
        maxsize = min(maxsize.value,self.peng.cfg["rsrc.maxtexsize"]) # This is here to avoid massive memory overhead when only loading a few textures
        self.texsize = maxsize

        # name is always [category][name] here
        self.categories = {}  # Maps from name -> TextureRegion
        self.categoriesTexCache = {}  # Maps from name -> target,texid,texcoords
        self.categoriesTexBin = {}  # Maps from name -> TextureBin
        self.categoriesSettings = {}  # Maps from name -> settings dict
        self.categoriesSizes = {}  # Maps from name -> size
        
        self.missingTexture = None
        
        self.modelcache = {}
        self.modelobjcache = {}
        
        self.peng.sendEvent("peng3d:rsrc.init",{"peng":self.peng,"rsrcMgr":self})
        
    def resourceNameToPath(self,name,ext=""):
        """
        Converts the given resource name to a file path.
        
        A resource path is of the format ``<app>:<cat1>.<cat2>.<name>`` where cat1 and cat2 can be repeated as often as desired.
        
        ``ext`` is the file extension to use, e.g. ``.png`` or similar.
        
        As an example, the resource name ``peng3d:some.category.foo`` with the extension ``.png`` results in the path ``<basepath>/assets/peng3d/some/category/foo.png``\\ .
        
        This resource naming scheme is used by most other methods of this class.
        
        Note that it is currently not possible to define multiple base paths to search through.
        """
        nsplit = name.split(":")[1].split(".")
        return os.path.join(self.basepath,"assets",name.split(":")[0],*nsplit)+ext
    def resourceExists(self,name,ext=""):
        """
        Returns whether or not the resource with the given name and extension exists.
        
        This must not mean that the resource is meaningful, it simply signals that the file exists.
        """
        return os.path.exists(self.resourceNameToPath(name,ext))
    def addCategory(self,name, size=None):
        """
        Adds a new texture category with the given name.
        
        If the category already exists, it will be overridden.
        """
        if size is None:
            size = self.texsize

        self.categories[name]={}
        self.categoriesSettings[name] = {
            "magfilter": GL_NEAREST,
            "minfilter": GL_NEAREST_MIPMAP_LINEAR,
        }
        self.categoriesSizes[name] = {}
        self.categoriesTexCache[name]={}
        self.categoriesTexBin[name]=pyglet.image.atlas.TextureBin(size, size)
        self.peng.sendEvent("peng3d:rsrc.category.add", {"peng": self.peng, "category": name})
    def getTex(self,name,category):
        """
        Gets the texture associated with the given name and category.
        
        ``category`` must have been created using :py:meth:`addCategory()` before.
        
        If it was loaded previously, a cached version will be returned.
        If it was not loaded, it will be loaded and inserted into the cache.
        
        See :py:meth:`loadTex()` for more information.
        """
        if category not in self.categoriesTexCache:
            self.peng.sendEvent("peng3d:rsrc.missing.category", {"cat": category, "name": name})
            return self.getMissingTex(category)
        if name not in self.categoriesTexCache[category]:
            self.loadTex(name,category)
        return self.categoriesTexCache[category][name]
    def loadTex(self,name,category):
        """
        Loads the texture of the given name and category.
        
        All textures currently must be PNG files, although support for more formats may be added soon.
        
        If the texture cannot be found, a missing texture will instead be returned. See :py:meth:`getMissingTexture()` for more information.
        
        Currently, all texture mipmaps will be generated and the filters will be set to
        :py:const:`GL_NEAREST` for the magnification filter and :py:const:`GL_NEAREST_MIPMAP_LINEAR` for the minification filter.
        This results in a pixelated texture and not  a blurry one.
        """
        try:
            img = pyglet.image.load(self.resourceNameToPath(name,".png"))
        except FileNotFoundError:
            self.peng.sendEvent("peng3d:rsrc.missing.tex", {"cat": category, "name": name})
            img = self.getMissingTexture()
        texreg = self.categoriesTexBin[category].add(img)
        #texreg = texreg.get_transform(True,True) # Mirrors the image due to how pyglets coordinate system works
        # Strange behavior, sometimes needed and sometimes not
        self.categories[category][name]=texreg
        self.categoriesSizes[category][name] = img.width, img.height
        target = texreg.target
        texid = texreg.id
        texcoords = texreg.tex_coords
        # Prevents texture bleeding with texture sizes that are powers of 2, else weird lines may appear at certain angles.
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.categoriesSettings[category]["magfilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.categoriesSettings[category]["minfilter"])
        glGenerateMipmap(GL_TEXTURE_2D)
        
        out = target,texid,texcoords
        self.categoriesTexCache[category][name]=out
        self.peng.sendEvent("peng3d:rsrc.tex.load",{"peng":self.peng,"name":name,"category":category})
        return out
    def getMissingTexture(self):
        """
        Returns a texture to be used as a placeholder for missing textures.
        
        A default missing texture file is provided in the assets folder of the source distribution.
        It consists of a simple checkerboard pattern of purple and black, this image may be copied to any project using peng3d for similar behavior.
        
        If this texture cannot be found, a pattern is created in-memory, simply a solid square of purple.
        
        This texture will also be cached separately from other textures.
        """
        if self.missingTexture is None:
            if self.resourceExists(self.missingtexturename,".png"):
                self.missingTexture = pyglet.image.load(self.resourceNameToPath(self.missingtexturename,".png"))
                return self.missingTexture
            else: # Falls back to create pattern in-memory
                self.missingTexture = pyglet.image.create(1,1,pyglet.image.SolidColorImagePattern([255,0,255,255]))
                return self.missingTexture
        else:
            return self.missingTexture
    def getMissingTex(self,cat):
        if cat not in self.categories:
            self.addCategory(cat)
        return self.loadTex(self.missingtexturename,cat)
    def addFromTex(self,name,img,category):
        """
        Adds a new texture from the given image.
        
        ``img`` may be any object that supports Pyglet-style copying in form of the ``blit_to_texture()`` method.
        
        This can be used to add textures that come from non-file sources, e.g. Render-to-texture.
        """
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

    def normTex(self, dat, default_cat=None):
        if isinstance(dat, str):
            if default_cat is None:
                raise ValueError("default_cat cannot be None if a string is given")
            return self.getTex(dat, default_cat)
        elif isinstance(dat, list) or isinstance(dat, tuple):
            if len(dat) == 2:
                # Tuple of name, cat
                return self.getTex(dat[0], dat[1])
            elif len(dat) == 3:
                return dat  # Already a texture 3-tupel
            else:
                raise TypeError("Invalid length list/tuple")
        else:
            raise TypeError("Invalid type for normTex")

    def getTexSize(self, name, category):
        if name not in self.categoriesSizes[category]:
            self.loadTex(name, category)
        return self.categoriesSizes[category][name]
    
    def getModel(self,name):
        """
        Gets the model object by the given name.
        
        If it was loaded previously, a cached version will be returned.
        If it was not loaded, it will be loaded and inserted into the cache.
        """
        if name in self.modelobjcache:
            return self.modelobjcache[name]
        return self.loadModel(name)
    def loadModel(self,name):
        """
        Loads the model of the given name.
        
        The model will also be inserted into the cache.
        """
        m = model.Model(self.peng,self,name)
        self.modelobjcache[name]=m
        self.peng.sendEvent("peng3d:rsrc.model.load",{"peng":self.peng,"name":name})
        return m
    
    def getModelData(self,name):
        """
        Gets the model data associated with the given name.
        
        If it was loaded, a cached copy will be returned.
        It it was not loaded, it will be loaded and cached.
        """
        if name in self.modelcache:
            return self.modelcache[name]
        return self.loadModelData(name)
    def loadModelData(self,name):
        """
        Loads the model data of the given name.
        
        The model file must always be a .json file.
        """
        path = self.resourceNameToPath(name,".json")
        try:
            data = json.load(open(path,"r"))
        except Exception:
            # Temporary
            print("Exception during model load: ")
            import traceback;traceback.print_exc()
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
