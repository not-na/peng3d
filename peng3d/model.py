#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  model.py
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

import time

import math
from math import sqrt,cos,sin

try:
    from itertools import zip_longest
except ImportError:
    pass # probably on readthedocs

try:
    import pyglet
    from pyglet.gl import *
except ImportError:
    pass # probably headless

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def calcSphereCoordinates(pos,radius,rot):
    # Input angles should be in degrees, as in the rest of the game
    # E.g. phi=inclination and theta=azimuth
    
    # phi is yrad
    #      Look from above         
    #(Z goes positive towards you) 
    #                              
    #            Y-  Z-            
    #            |  /              
    #            | / "far"         
    #            |/                
    #   X- ------+-------> X+      
    #           /| yrad |          
    #   "near" / |<-----+          
    #         /  |  "polar angle"  
    #        Z+  Y+                
    
    # theta is xrad
    #      Look from above         
    #(Z goes positive towards you) 
    #                              
    #            Y-  Z-            
    #            |  /              
    #            | / "far"         
    #            |/                
    #   X- ------+-------> X+      
    #           /| xrad |          
    #   "near" /<-------+          
    #         /  |  "azimuth angle"
    #        Z+  Y+                

    # Based on http://stackoverflow.com/questions/39647735/calculation-of-spherical-coordinates
    # https://en.wikipedia.org/wiki/Spherical_coordinate_system
    # http://stackoverflow.com/questions/25404613/converting-spherical-coordinates-to-cartesian?rq=1
    
    phi,theta = rot
    phi+=90 # very important, took me four days of head-scratching to figure out
    phi,theta = math.radians(phi),math.radians(theta)
    
    x = pos[0]+radius * math.sin(phi) * math.cos(theta)
    y = pos[1]+radius * math.sin(phi) * math.sin(theta)
    z = pos[2]+radius * math.cos(phi)
    return x,y,z

def v_magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def v_normalize(v,d=None):
    vmag = v_magnitude(v)
    print(vmag,v,d)
    return [ v[i]/vmag  for i in range(len(v)) ]

class Material(object):
    def __init__(self,rsrcMgr,name,matdata):
        self.rsrcMgr = rsrcMgr
        
        self.name = name
        self.matdata = matdata
        
        self.texname = matdata.get("tex","peng3d:missingtexture")
        self.texcat = matdata.get("texcat","entity")
        if self.texcat not in self.rsrcMgr.categories:
            self.rsrcMgr.addCategory(self.texcat)
        
    @property
    def target(self):
        return self.rsrcMgr.getTex(self.texname,self.texcat)[0]
    @property
    def id(self):
        return self.rsrcMgr.getTex(self.texname,self.texcat)[1]
    @property
    def tex_coords(self):
        return self.rsrcMgr.getTex(self.texname,self.texcat)[2]
    
    @property
    def texdata(self):
        return self.rsrcMgr.getTex(self,texname,self.texcat)
    
    def transformTexCoords(self,data,texcoords,dims=2):
        assert dims==2 # TODO
        
        out = []
        
        origcoords = self.tex_coords
        min_u,min_v = origcoords[0],origcoords[1]
        max_u,max_v = origcoords[6],origcoords[7]
        
        diff_u,diff_v = max_u-min_u, max_v-min_v

        itexcoords = iter(texcoords)
        for u,v in zip(itexcoords,itexcoords): # Based on http://stackoverflow.com/a/5389547/3490549
            out_u = min_u+(diff_u*u)
            out_v = min_v+(diff_v*v)
            out.extend((out_u,out_v,0))
        
        return out # output dimensionality is 3, e.g. t3f

class Bone(object):
    def __init__(self,rsrcMgr,name,bonedata):
        self.rsrcMgr = rsrcMgr
        
        self.name = name
        self.bonedata = bonedata
        
        self.regions = {}
        self.child_bones = {}
        
        self.parent = None
        self.start_rot = bonedata.get("start_rot",[0,0])
        self.blength = bonedata.get("length",1.0)
    
    def ensureBones(self,data):
        if "_bones" not in data:
            data["_bones"]={}
        if self.name not in data["_bones"]:
            data["_bones"][self.name]={"rot":self.start_rot[:],"length":self.blength}
    
    def setRot(self,data,rot):
        self.ensureBones(data)
        rot = rot[0]%360,max(-90, min(90, rot[1]))
        self.updateOnRot(data,data["_bones"][self.name]["rot"],rot)
        data["_bones"][self.name]["rot"]=rot
    def getRot(self,data):
        self.ensureBones(data)
        return data["_bones"][self.name]["rot"]
    
    def setLength(self,data,blength):
        self.ensureBones(data)
        self.updateOnLength(data,data["_bones"][self.name]["length"],blength)
        data["_bones"][self.name]["length"]=blength
    def getLength(self,data):
        self.ensureBones(data)
        return data["_bones"][self.name]["length"]
    
    def setParent(self,parent):
        self.parent = parent
        self.parent.child_bones[self.name]=self
    
    def setRotate(self,data):
        self.parent.setRotate(data)
        glPushMatrix()
        x,y = self.getRot(data)
        pivot = self.getPivotPoint(data)
        px,py,pz = pivot

        #ppx,ppy,ppz = self.parent.getPivotPoint(data)
        #rot_vec = px-ppx,py-ppy,pz-ppz
        #print([px,py,pz],[ppx,ppy,ppz],rot_vec,[x,y],self.getLength(data))
        #norm = v_normalize(rot_vec,self.name) if v_magnitude(rot_vec)==0 else [0,1,0] # prevents a zero divison error
        normx = [0,1,0] # currently fixed to the up vector, should be changed in the future for proper rotation that is not along the y or z axis
        normy = [0,0,1]
        
        #offset = -px,-py,-pz
        
        glTranslatef(px,py,pz)#-offset[0],-offset[1],-offset[2])
        glRotatef(x-self.start_rot[0], normx[0],normx[1],normx[2])
        glRotatef(y-self.start_rot[1], normy[0],normy[1],normy[2])
        glTranslatef(-px,-py,-pz)#offset[0],offset[1],offset[2])
    def unsetRotate(self,data):
        glPopMatrix()
        self.parent.unsetRotate(data)
    
    def updateOnRot(self,data,old,new):
        pass
    
    def getPivotPoint(self,data):
        ppos = self.parent.getPivotPoint(data)
        rot = self.parent.getRot(data)
        length = self.parent.getLength(data)
        out = calcSphereCoordinates(ppos,length,rot)
        return out
    
    def updateOnLength(self,data,old,new):
        pass # currently not implemented
    
    def getOffset(self,data):
        offset = self.parent.getOffset(data)
        return calcSphereCoordinates(offset,self.blength,self.getDeltaRot(data))
    
    def offsetVertices(self,data,vertices,dims=3):
        assert dims==3
        ox,oy,oz = self.getOffset(data)
        
        out = []
        for x,y,z in zip(*[iter(vertices)]*3):
            vertex = x+ox,y+oy,z+oz
            out.extend(vertex)
        
        return out
        
    def transformVertices(self,data,vertices,dims=3):
        assert dims==3
        
        # vertices are not transformed directly, rather they are rotated dynamically via glRotate
        
        return vertices 
    
    def addRegion(self,region):
        self.regions[region.name]=region

class RootBone(Bone):
    def getPivotPoint(self,data):
        return [0,0,0]
    def getLength(self,data):
        return 0
    def setRotate(self,data):
        pass # no rotation as the root bone is always pointed straight up
    def unsetRotate(self,data):
        pass # no unset as there is no set

class Region(object):
    def __init__(self,rsrcMgr,name,regdata):
        self.rsrcMgr = rsrcMgr
        
        self.name = name
        self.regdata = regdata
        
        self.material = None
        self.bone = None
        
        self.dims = 3
        self.tex_dims = 2
        
        gtype = regdata.get("geometry_type","quads")
        if gtype in ["quads","quad","GL_QUADS"]:
            self.geometry_type = GL_QUADS
            # points per primitive
            ppp = 4
        elif gtype in ["tris","triangles","triangle","GL_TRIANGLES"]:
            self.geometry_type = GL_TRIANGLES
            ppp = 3
        elif gtype in ["lines","line","GL_LINES"]:
            self.geometry_type = GL_LINES
            ppp = 2
        elif gtype in ["points","point","dots","dot","GL_POINTS"]:
            self.geometry_type = GL_POINTS
            ppp = 1
        else:
            raise ValueError("Invalid Geometry type %s"%gtype)
        
        self.vertices = regdata.get("vertices",[])
        if len(self.vertices)%self.dims!=0:
            raise ValueError("Vertices must be in x,y,z groups")
        elif (len(self.vertices)/self.dims)%ppp!=0:
            raise ValueError("Invalid amount of x,y,z groups, must be integer-divisible by %s"%ppp)
        
        if "tex_coords" in regdata:
            self.enable_tex = True
            self.tex_coords = regdata.get("tex_coords",[])
            if len(self.tex_coords)/self.tex_dims!=len(self.vertices)/self.dims:
                raise ValueError("Non-Matching amount of vertices and tex coords")
            elif len(self.tex_coords)%self.tex_dims!=0:
                raise ValueError("Tex coords must be in u,v pairs")
            elif (len(self.tex_coords)/self.tex_dims)%ppp!=0:
                raise ValueError("Invalid amount of u,v pairs, must be integer-divisible by %s"%ppp)
        else:
            self.enable_tex = False
            self.tex_coords = [0]*(self.tex_dims*(len(self.vertices)/self.dims))
    
    def getVertices(self,data):
        return self.bone.transformVertices(data,self.vertices,self.dims)
    def getGeometryType(self,data):
        return self.geometry_type
    def getTexCoords(self,data):
        return self.material.transformTexCoords(data,self.tex_coords,self.tex_dims)
    def getTexInfo(self,data):
        return self.material.texdata

class Animation(object):
    def __init__(self,rsrcMgr,name,anidata):
        self.rsrcMgr = rsrcMgr
        
        self.name = name
        self.anidata = anidata
        
        self.bones = {}
        
        self.atype = anidata.get("type","bone" if "keyframes" in anidata else "static")
        
        self.default_jt = anidata.get("default_jumptype","animate")
        
        self.entity_defaults = {}
        self.entity_template = {}
        
        if self.atype == "static":
            self.start_frame = {"bones":anidata.get("bones")}
        elif self.atype == "keyframes":
            self.kps = anidata.get("keyframespersecond",60)
            self.anilength = anidata.get("length",self.kps)
            
            self.lframes_per_bone = {} # for length-setting keyframes
            self.rframes_per_bone = {} # for rotating keyframes
            
            minframe = None
            for frame,keyframe in anidata.get("keyframes",{}).items():
                frame = int(frame)
                if minframe is None or frame<minframe:
                    minframe = frame
                
                for bname,bone in keyframe.get("bones",{}).items():
                    if "rot" in bone:
                        if bname not in self.rframes_per_bone:
                            self.rframes_per_bone[bname]={}
                        self.rframes_per_bone[bname][frame]=bone["rot"]
                    if "length" in bone:
                        if bname not in self.lframes_per_bone:
                            self.lframes_per_bone[bname]={}
                        self.lframes_per_bone[bname][frame]=bone["length"]
            
            self.start_frame = anidata["keyframes"][str(minframe)] if minframe is not None else {"bones":{}}
            self.start_frame["frame"] = minframe if minframe is not None else 0
        else:
            raise ValueError("Invalid animation type %s for animation %s"%(self.atype,name))
    
    def setBones(self,bones):
        self.bones = bones
    
    def startAnimation(self,data,jumptype):
        data["_anidata"]={}
        adata = data["_anidata"]
        
        adata["keyframe"]=0
        adata["last_tick"]=time.time()
        adata["jumptype"]=jumptype
        adata["phase"]="transition"
    
    def tickEntity(self,data):
        adata = data["_anidata"]
        
        if adata.get("anitype",self.name)!=self.name:
            return # incorrectly called
        
        dt = time.time()-adata.get("last_tick",time.time())
        adata["last_tick"]=time.time()
        
        if adata.get("phase","transition")=="transition":
            # If transitioning to this animation
            if adata.get("jumptype",self.default_jt)=="jump":
                # Jumping to the animation, e.g. set all bones to the start frame
                for bone,dat in self.start_frame.get("bones",{}).items():
                    if "rot" in dat:
                        self.bones[bone].setRot(data,dat["rot"])
                    if "length" in dat:
                        self.bones[bone].setLength(data,dat["length"])
                adata["phase"]="animation"
                if self.atype=="keyframes":
                    adata["from_frame"]=self.start_frame.get("frame",0)
            elif adata.get("jumptype",self.default_jt)=="animate":
                raise NotImplementedError("Animation update phase transition type animate not yet implemented")
                
                # Not yet working
                if "transition_frame" not in adata:
                    adata["transition_frame"] = 0
                tlen = self.anidata.get("transition_length",self.anidata.get("length",60)/3)
                tspeed = self.anidata.get("transition_speed",self.anidata.get("keyframespersecond",60))
                
                framediff=int(dt/(1./tspeed)) # Number of frames that have passed since the last update
                overhang = dt-(framediff*(1./tspeed)) # time that has passed but is not enough for a full frame
                adata["last_tick"]-=overhang # causes the next frame to include the overhang from this frame
                if framediff == 0:
                    return # optimization that saves time 
                
                frame1 = adata["transition_frame"]
                adata["transition_frame"]+=framediff
                if adata["transition_frame"]>tlen:
                    adata["phase"]="animation"
                    if self.atype=="keyframes":
                        adata["from_frame"]=self.start_frame.get("frame",0)
                    return
                frame2 = adata["transition_frame"]
                
                if "frombones" not in adata:
                    frombones = {}
                    for bname,bone in self.bones.items():
                        frombones[bname]={"rot":bone.getRot(data),"length":bone.getLength(data)}
                    adata["frombones"] = frombones
                if "tobones" not in adata:
                    tobones = {}
                    for bname,bone in self.start_frame["bones"].items():
                        tobones[bname]=bone
                    adata["tobones"] = tobones
                
                frombones = adata["frombones"]
                tobones = adata["tobones"]
                
                from_frame = 0
                to_frame = tlen
                
                for bname,bone in self.bones.items():
                    # rot
                    if bname not in frombones or bname not in tobones:
                        continue
                    
                    from_rot = frombones[bname]["rot"]
                    to_rot = tobones[bname]["rot"]
                    
                    from_x,from_y=from_rot
                    to_x,to_y=to_rot
                    
                    delta_per_frame_x = (to_x-from_x)/(to_frame-from_frame)
                    delta_per_frame_y = (to_y-from_y)/(to_frame-from_frame)
                    
                    delta_x = delta_per_frame_x*(frame2-frame1)
                    delta_y = delta_per_frame_y*(frame2-frame1)
                    
                    rot = bone.getRot(data)
                    new_rot = [rot[0]+delta_x,rot[1]+delta_y]
                    
                    bone.setRot(data,new_rot)
                    
                    # length
                    
                    # Not yet implemented
                
        elif adata["phase"]=="animation":
            # If animating
            if self.atype == "static":
                pass # Should not need any updates as the transition will set the bones
            elif self.atype == "keyframes":
                framediff=int(dt/(1./self.kps)) # Number of frames that have passed since the last update
                overhang = dt-(framediff*(1./self.kps)) # time that has passed but is not enough for a full frame
                adata["last_tick"]-=overhang # causes the next frame to include the overhang from this frame
                if framediff == 0:
                    return # optimization that saves time 
                
                frame1 = adata["keyframe"]
                adata["keyframe"]+=framediff
                if adata["keyframe"]>self.anilength:
                    repeat = True
                    adata["keyframe"]%=self.anilength
                else:
                    repeat = False
                frame2 = adata["keyframe"]
                
                if repeat:
                    frame1 = frame2
                    frame2+=1
                
                for bname,bone in self.bones.items():
                    # Rot
                    if bname in self.rframes_per_bone:
                        
                        from_frame = None#adata["from_frame"]
                        to_frame = None
                        for framenum,rot in self.rframes_per_bone[bname].items():
                            if (from_frame is None or framenum>from_frame) and framenum<=frame1:
                                # from_frame is the largest frame number that is before the starting point
                                from_frame = framenum
                            if (to_frame is None or framenum<to_frame) and framenum>=frame2:
                                # to_frame is the smallest frame number that is after the end point
                                to_frame = framenum
                        if from_frame is None or to_frame is None:
                            raise ValueError("Invalid frames for bone %s in animation %s"%(bname,self.name))
                        if from_frame==to_frame or repeat:
                            if self.anidata.get("repeat","jump")=="jump":
                                for b,dat in self.start_frame.get("bones",{}).items():
                                    if "rot" in dat:
                                        self.bones[b].setRot(data,dat["rot"])
                                    if "length" in dat:
                                        self.bones[b].setLength(data,dat["length"])
                            elif self.anidata.get("repeat","jump")=="animate":
                                from_frame = adata["to_frame"]
                        adata["from_frame"]=from_frame
                        adata["to_frame"]=to_frame
                        
                        from_rot = self.rframes_per_bone[bname][from_frame]
                        to_rot = self.rframes_per_bone[bname][to_frame]
                        
                        from_x,from_y=from_rot
                        to_x,to_y=to_rot
                        
                        if self.anidata.get("interpolation","linear") == "linear":
                            delta_per_frame_x = (to_x-from_x)/(to_frame-from_frame)
                            delta_per_frame_y = (to_y-from_y)/(to_frame-from_frame)
                            
                            delta_x = delta_per_frame_x*(frame2-frame1)
                            delta_y = delta_per_frame_y*(frame2-frame1)
                            
                            rot = bone.getRot(data)
                            new_rot = [rot[0]+delta_x,rot[1]+delta_y]
                        elif self.anidata["interpolation"] == "jump":
                            new_rot = to_x,to_y
                        else:
                            raise ValueError("Invalid interpolation method '%s' for animation %s"%(self.anidata["interpolation"],self.name))
                        
                        bone.setRot(data,new_rot)
                        
                    # Length
                    if bname in self.lframes_per_bone:
                        # Not yet implemented
                        pass
                
            else:
                # Should not be possible, but still
                raise ValueError("Invalid animation type %s for animation %s during tick"%(self.atype,name))


class JSONModelGroup(pyglet.graphics.Group):
    def __init__(self,model,data,obj,parent=None):
        super(JSONModelGroup,self).__init__(parent)
        
        self.model = model
        self.data = data
        self.obj = obj
    
    def set_state(self):
        x,y,z = self.obj.pos
        glTranslatef(x,y,z)
    
    def unset_state(self):
        x,y,z = self.obj.pos
        glTranslatef(-x,-y,-z)
    
    def __hash__(self):
        return hash((tuple(self.obj.pos),))
    
    def __eq__(self,other):
        return (self.__class__ is other.__class__ and
                self.obj.pos == other.obj.pos and
                self.parent == other.parent
               )

class JSONRegionGroup(pyglet.graphics.Group):
    def __init__(self,model,data,region,parent=None):
        super(JSONRegionGroup,self).__init__(parent)
        
        self.model = model
        self.data = data
        self.region = region
    
    def set_state(self):
        glEnable(self.region.material.target)
        glBindTexture(self.region.material.target, self.region.material.id)
        self.region.bone.setRotate(self.data)
    
    def unset_state(self):
        glDisable(self.region.material.target)
        self.region.bone.unsetRotate(self.data)
    
    def __hash__(self):
        return hash((self.region.material.target, self.region.material.id, self.parent))

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
            self.region.material.target == other.region.material.target and
            self.region.material.id == other.region.material.id and
            self.region.bone is other.region.bone and
            self.region.bone.getRot(self.data) == other.region.bone.getRot(other.data) and
            self.region.bone.getLength(self.data) == other.region.bone.getLength(other.data) and # TODO: include parent bones
            self.parent == other.parent
            )


class Model(object):
    def __init__(self,peng,rsrcMgr,name):
        self.peng = peng
        self.rsrcMgr = rsrcMgr
        self.name = name
        
        self.modeldata = self.rsrcMgr.getModelData(name)
    
    def ensureModelData(self,obj):
        if not hasattr(obj,"_modeldata"):
            self.create(obj,cache=True)
        if "_modelcache" not in obj._modeldata:
            # Assume all initialization is missing, simply reinitialize
            self.create(obj,cache=True)
    
    def create(self,obj,cache=False):
        obj._modeldata = {}
        
        data = obj._modeldata
        
        data["_model"]=self
        data["_modelcache"] = {}
        moddata = data["_modelcache"]
        
        # Model group, for pos of entity
        moddata["group"] = JSONModelGroup(self,data,obj)
        modgroup = moddata["group"]
        
        if not hasattr(obj,"batch3d"):
            obj.batch3d = pyglet.graphics.Batch()
            data["_manual_render"]=True
        
        # Vlists/Regions
        moddata["vlists"] = {}
        for name,region in self.modeldata["regions"].items():
            v = region.getVertices(data)
            vlistlen = int(len(v)/region.dims)
            
            if region.enable_tex:
                vlist = obj.batch3d.add(vlistlen,region.getGeometryType(data),JSONRegionGroup(self,data,region,modgroup),
                        "v3f/static",
                        "t3f/static",
                        )
            else:
                vlist = obj.batch3d.add(vlistlen,region.getGeometryType(data),modgroup,
                        "v3f/static",
                        )
            
            moddata["vlists"][name]=vlist
        
        self.setAnimation(obj,self.modeldata["default_animation"].name,transition="jump")
        
        self.data = data
        
        if not cache:
            self.redraw(obj)
    
    def cleanup(self,obj):
        if not hasattr(obj,"_modeldata"):
            return # already not initialized
        data = obj._modeldata
        
        if "_modelcache" in data:
            moddata = data["_modelcache"]
            
            if "vlists" in moddata:
                for vlist in list(moddata["vlists"].keys()):
                    del moddata["vlists"][vlist]
                del moddata["vlists"]
        
        if "_bones" in data:
            for bone in list(data["_bones"].keys()):
                del data["_bones"][bone]
            del data["_bones"]
        
        if "_anidata" in data:
            adata = data["_anidata"]
            if "_schedfunc" in adata:
                pyglet.clock.unschedule(adata["_schedfunc"])
        
        if data.get("_manual_render",False):
            del obj.batch3d
        
        # Removes open vertex lists and other caches
        
        if "_modelcache" not in data:
            return
        moddata = data["_modelcache"]
        
        if "vlist" in moddata:
            moddata["vlist"].delete() # Free up the graphics memory
        if "group" in moddata:
            del moddata["group"]
        
        del data["_modelcache"], moddata
    
    def redraw(self,obj):
        self.ensureModelData(obj)
        data = obj._modeldata
        
        vlists = data["_modelcache"]["vlists"]
        
        for name,region in self.modeldata["regions"].items():
            vlists[name].vertices = region.getVertices(data)
            if region.enable_tex:
                vlists[name].tex_coords = region.getTexCoords(data)
    
    def draw(self,obj):
        self.ensureModelData(obj)
        
        data = obj._modeldata
        if data.get("_manual_render",False):
            obj.batch3d.draw()
    
    def remove(self,obj):
        # Can be extended, but the base class should always be called
        self.cleanup(obj)
    
    def setAnimation(self,obj,animation,transition=None,force=False):
        self.ensureModelData(obj)
        data = obj._modeldata
        
        # Validity check
        if animation not in self.modeldata["animations"]:
            raise ValueError("There is no animation of name '%s' for model '%s'"%(animation,self.modelname))
        
        if data.get("_anidata",{}).get("anitype",None)==animation and not force:
            return # animation is already running
        
        # Cache the obj to improve readability
        anim = self.modeldata["animations"][animation]
        
        # Set to default if not set
        if transition is None:
            transition = anim.default_jt
        
        # Notify the animation to allow it to initialize itself
        anim.startAnimation(data,transition)
        
        # initialize animation data
        if "_anidata" not in data:
            data["_anidata"]={}
        adata = data["_anidata"]
        adata["anitype"]=animation
        
        if "_schedfunc" in adata:
            # unschedule the old animation, if any
            # prevents clashing and crashes
            pyglet.clock.unschedule(adata["_schedfunc"])
        
        # Schedule the animation function
        def schedfunc(*args):
            # This function is defined locally to create a closure
            # The closure stores the local variables, e.g. anim and data even after the parent function has finished
            # Note that this may also prevent the garbage collection of any objects defined in the parent scope
            anim.tickEntity(data)
        
        # register the function to pyglet
        pyglet.clock.schedule_interval(schedfunc,1./(anim.kps if anim.atype=="keyframes" else 60))
        # save it for later for de-initialization
        adata["_schedfunc"] = schedfunc
