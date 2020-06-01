#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  layered.py
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
import inspect
import weakref

__all__ = [
    "LayeredWidget",
    "BasicWidgetLayer","WidgetLayer",
    "GroupWidgetLayer",
    "ImageWidgetLayer","DynImageWidgetLayer",
    "FramedImageWidgetLayer",
    "ImageButtonWidgetLayer",
    "LabelWidgetLayer",
    "FormattedLabelWidgetLayer","HTMLLabelWidgetLayer",
    "BaseBorderWidgetLayer","ButtonBorderWidgetLayer",
    ]

import warnings

import pyglet
from pyglet.gl import *

from .widgets import Background, Widget
from .. import util

class LayeredWidget(Widget):
    """
    Layered Widget allowing for easy creation of custom widgets.
    
    A Layered Widget consists of (nearly) any amount of layers in a specific order.
    
    All Layers should be subclasses of :py:class:`BasicWidgetLayer` or :py:class:`WidgetLayer`\ .
    
    ``layers`` must be a list of 2-tuples of ``(layer,z_index)``\ .
    """

    IS_CLICKABLE = True
    def __init__(self,name,submenu,window,peng,
                pos=None,size=None,
                bg=None,layers=[],
                ):
        super(LayeredWidget,self).__init__(name,submenu,window,peng,pos,size,bg)
        
        self.layers = []
        self._layers = {}
        for l,z in layers:
            # Makes sure that all layers are sorted
            # Does not use sort() to keep original order
            self.addLayer(l,z)
    def addLayer(self,layer,z_index=None):
        """
        Adds the given layer at the given Z Index.
        
        If ``z_index`` is not given, the Z Index specified by the layer will be used.
        """
        if z_index is None:
            z_index = layer.z_index
        i = 0
        for l,z in self.layers:
            if z>z_index:
                break
            i+=1
        self._layers[layer.name]=layer
        self.layers.insert(i,[layer,z_index])
    def getLayer(self,name):
        """
        Returns the layer corresponding to the given name.
        
        :raises KeyError: If there is no Layer with the given name.
        """
        return self._layers[name]
    def on_redraw(self):
        super(LayeredWidget,self).on_redraw()
        for layer,_ in self.layers:
            layer.on_redraw()
    def redraw_layer(self,name):
        """
        Redraws the given layer.
        
        :raises ValueError: If there is no Layer with the given name.
        """
        if name not in self._layers:
            raise ValueError("Layer %s not part of widget, cannot redraw")
        self._layers[name].on_redraw()
    def draw(self):
        """
        Draws all layers of this LayeredWidget.
        
        This should normally be unneccessary, since it is recommended that layers use Vertex Lists instead of OpenGL Immediate Mode.
        """
        super(LayeredWidget,self).draw()
        for layer,_ in self.layers:
            layer._draw()
    def delete(self):
        """
        Deletes all layers within this LayeredWidget before deleting itself.
        
        Recommended to call if you are removing the widget, but not yet exiting the interpreter.
        """
        for layer,_ in self.layers:
            layer.delete()
        self.layers = []
        self._layers = {}
        super(LayeredWidget,self).delete()

class BasicWidgetLayer(object):
    """
    Base class for all Layers to be used with :py:class:`LayeredWidget()`\ .
    
    Not to be confused with :py:class:`peng3d.layer.Layer()`\ , these classes are not compatible.
    
    It is recommended to use :py:class:`WidgetLayer()` instead, since functionality is limited in this basic class.
    
    Note that the ``z_index`` will default to a reasonable value for most subclasses and thus is not required to be given explicitly.
    The ``z_index`` for this Layer defaults to ``0``\ .
    """
    z_index = 0
    def __init__(self,name,widget,
                z_index=None,
                ):
        self.name = name
        self.widget = widget
        
        if z_index is not None:
            self.z_index = z_index
        self.group = pyglet.graphics.OrderedGroup(self.z_index)
        
        self._vlists = []
    
    def on_redraw(self):
        """
        Called by the parent widget if this Layer should be redrawn.
        
        Note that it is recommended to call the Baseclass Variant of this Method first when overwriting it.
        See :py:meth:`WidgetLayer.on_redraw` for more information.
        """
        pass
    def _draw(self):
        self.predraw()
        self.draw()
        self.postdraw()
    
    def predraw(self):
        """
        Called before calling the :py:meth:`draw()` Method.
        
        Useful for setting up OpenGL state.
        """
        pass
    def draw(self):
        """
        Called to draw the layer.
        
        Note that using this function is discouraged, use Pyglet Vertex Lists instead.
        
        If you want to call this method manually, call :py:meth:`_draw()` instead.
        This will make sure that :py:meth:`predraw()` and :py:meth:`postdraw()` are called.
        """
        pass
    def postdraw(self):
        """
        Called after calling the :py:meth:`draw()` Method.
        
        Useful for unsetting OpenGL state.
        """
        pass
    
    def regVList(self,vlist):
        """
        Registers a vertex list for proper deletion once this Layer gets destroyed.
        
        This prevents visual artifacts from forming during deletion of a layer.
        """
        self._vlists.append(vlist)
    def delete(self):
        """
        Deletes this Layer.
        
        Currently only deletes VertexLists registered with :py:meth:`regVList()`\ .
        """
        for vlist in self._vlists:
            vlist.delete()
        self._vlists = []

        for e_type,e_handlers in self.widget.peng.eventHandlers.items():
            if True or e_type in eh:
                to_del = []
                for e_handler in e_handlers:
                    # Weird workaround due to implementation details of WeakMethod
                    if isinstance(e_handler,weakref.ref):
                        if super(weakref.WeakMethod,e_handler).__call__() is self:
                            to_del.append(e_handler)
                    elif e_handler is self:
                        to_del.append(e_handler)
                for d in to_del:
                    try:
                        #print("Deleting handler %s of type %s"%(d,e_type))
                        del e_handlers[e_handlers.index(d)]
                    except Exception:
                        #print("Could not delete handler %s, memory leak may occur"%d)
                        import traceback;traceback.print_exc()

        for eframe in self.widget.peng.window._event_stack:
            for e_t, e_m in eframe.items():
                if inspect.ismethod(e_m) and dict(inspect.getmembers(e_m))["__self__"] == self:
                    self.widget.peng.window.remove_handler(e_t, e_m)

class WidgetLayer(BasicWidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer()` adding commonly used utility features.
    
    This subclass adds a border and offset system.
    
    The ``border`` is a 2-tuple of ``(x_border,y_border)``\ . The border is applied to all sides, resulting in the size being decreased by two pixel per pixel border width.
    
    ``offset`` is relative to the bottom left corner of the screen.
    """
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                ):
        super(WidgetLayer,self).__init__(name,widget,z_index)
        
        self._initialized = False
        self._border = border
        self._offset = offset
    def on_redraw(self):
        """
        Called when the Layer should be redrawn.
        
        If a subclass uses the :py:meth:`initialize()` Method, it is very important to also call the Super Class Method to prevent crashes.
        """
        super(WidgetLayer,self).on_redraw()
        if not self._initialized:
            self.initialize()
            self._initialized = True
    def initialize(self):
        """
        Called just before :py:meth:`on_redraw()` is called the first time.
        """
        pass
    
    @property
    def border(self):
        """
        Property to be used for setting and getting the border of the layer.
        
        Note that setting this property causes an immediate redraw.
        """
        if callable(self._border):
            return util.WatchingList(self._border(*(self.widget.pos+self.widget.size)),self._wlredraw_border)
        else:
            return util.WatchingList(self._border,self._wlredraw_border)
    @border.setter
    def border(self,value):
        self._border = value
        self.on_redraw()
    
    @property
    def offset(self):
        """
        Property to be used for setting and getting the offset of the layer.
        
        Note that setting this property causes an immediate redraw.
        """
        if callable(self._offset):
            return util.WatchingList(self._offset(*(self.widget.pos+self.widget.size)),self._wlredraw_offset)
        else:
            return util.WatchingList(self._offset,self._wlredraw_offset)
    @offset.setter
    def offset(self,value):
        self._offset = value
        self.on_redraw()
    
    def _wlredraw_border(self,wl):
        self.border = wl[:]
    def _wlredraw_offset(self,wl):
        self.offset = wl[:]
    
    def getPos(self):
        """
        Returns the absolute position and size of the layer.
        
        This method is intended for use in vertex position calculation, as the border and offset have already been applied.
        
        The returned value is a 4-tuple of ``(sx,sy,ex,ey)``\ .
        The two values starting with an s are the "start" position, or the lower-left corner.
        The second pair of values signify the "end" position, or upper-right corner.
        """
        # Returns sx,sy,ex,ey
        # sx,sy are bottom-left/lowest
        # ex,ey are top-right/highest
        sx,sy = self.widget.pos[0]+self.border[0]+self.offset[0],                       self.widget.pos[1]+self.border[1]+self.offset[1]
        ex,ey = self.widget.pos[0]+self.widget.size[0]-self.border[0]+self.offset[0],   self.widget.pos[1]+self.widget.size[1]-self.border[1]+self.offset[1]
        return sx,sy,ex,ey
    def getSize(self):
        """
        Returns the size of the layer, with the border size already subtracted.
        """
        return self.widget.size[0]-self.border[0]*2,self.widget.size[1]-self.border[1]*2

class GroupWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer()` allowing for using a pyglet group to manage OpenGL state.
    
    If no pyglet group is given, :py:class:`pyglet.graphics.NullGroup()` will be used.
    """
    def __init__(self,name,widget,
                group=None,z_index=None,
                border=[0,0],offset=[0,0],
                ):
        super(GroupWidgetLayer,self).__init__(name,widget,z_index,border,offset)
        
        self.group = group if group is not None else pyglet.graphics.NullGroup()
    def predraw(self):
        self.group.set_state()
    predraw.__noautodoc__ = True
    def postdraw(self):
        self.group.unset_state()
    postdraw.__noautodoc__ = True

class ImageWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer()` implementing a simple static image view.
    
    This layer can display any resource representable by the :py:class:`ResourceManager()`\ .
    
    ``img`` is a 2-tuple of ``(resource_name,category)``\ .
    
    The ``z_index`` for this Layer defaults to ``1``\ .
    """
    z_index = 1
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                img=[None,None],
                ):
        super(ImageWidgetLayer,self).__init__(name,widget,z_index,border,offset)
        
        self.img = widget.peng.resourceMgr.getTex(*img)
        self.img_group = util.ResourceGroup(self.img,self.group)
    
    def initialize(self):
        self.img_vlist = self.widget.submenu.batch2d.add(4,GL_QUADS,self.img_group,
                        "v2f",
                        ("t3f",self.img[2]),
                        )
        self.regVList(self.img_vlist)
    initialize.__noautodoc__ = True
    def on_redraw(self):
        super(ImageWidgetLayer,self).on_redraw()
        sx,sy, ex,ey = self.getPos()
        
        # A simple rectangle
        self.img_vlist.vertices =  sx,sy, ex,sy, ex,ey, sx,ey

class _DynImageGroup(pyglet.graphics.Group):
    def __init__(self,layer,parent=None):
        super(_DynImageGroup,self).__init__(parent)
        self.layer = layer
    def set_state(self):
        tex_info = self.layer.imgs[self.layer.cur_img]
        glEnable(tex_info[0])
        glBindTexture(tex_info[0],tex_info[1])
    def unset_state(self):
        tex_info = self.layer.imgs[self.layer.cur_img]
        glDisable(tex_info[0])

class DynImageWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer` allowing for dynamic images.
    
    ``imgs`` is a dictionary of names to 2-tuples of ``(resource_name,category)``\ .
    
    If no default image name is given, a semi-random one will be selected.
    
    The ``z_index`` for this Layer defaults to ``1``\ .
    """
    z_index = 1
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                imgs={},
                default=None,
                ):
        super(DynImageWidgetLayer,self).__init__(name,widget,z_index,border,offset)
        
        self.imgs = {}
        self.img_group = _DynImageGroup(self,self.group)
        for name,rsrc in imgs.items():
            self.addImage(name,rsrc)
        
        self.cur_img = None
        self.default_img = default
    
    def addImage(self,name,rsrc):
        """
        Adds an image to the internal registry.
        
        ``rsrc`` should be a 2-tuple of ``(resource_name,category)``\ .
        """
        self.imgs[name]=self.widget.peng.resourceMgr.normTex(rsrc)
    def switchImage(self,name):
        """
        Switches the active image to the given name.
        
        :raises ValueError: If there is no such image
        """
        if name not in self.imgs:
            raise ValueError("No image of name '%s'"%name)
        elif self.cur_img==name:
            return
        
        self.cur_img = name
        self.on_redraw()
    
    def initialize(self):
        self.img_vlist = self.widget.submenu.batch2d.add(4,GL_QUADS,self.img_group,
                        "v2f",
                        "t3f",
                        )
        self.regVList(self.img_vlist)
        
        self.cur_img = self.cur_img if self.cur_img is not None else (self.default_img if self.default_img is not None else list(self.imgs.keys())[0])
    initialize.__noautodoc__ = True
    def on_redraw(self):
        super(DynImageWidgetLayer,self).on_redraw()
        sx,sy, ex,ey = self.getPos()
        
        # A simple rectangle
        self.img_vlist.vertices =  sx,sy, ex,sy, ex,ey, sx,ey
        
        self.img_vlist.tex_coords = self.imgs[self.cur_img][2]


class FramedImageWidgetLayer(DynImageWidgetLayer):
    """
    Subclass of :py:class:`DynImageWidgetLayer` allowing for dynamically smart scaled images.

    Similar to :py:class:`FramedImageButton`\\ . Allows for scaling and/or repeating
    the borders, corners and center independently.

    Note that the ``tex_size`` parameter, if not given, will be derived from a random texture
    that has been given in ``imgs``\\ . Also note that the ``frame``\\ , ``scale``\\ ,
    ``repeat_edge`` and ``repeat_center`` parameters are identical for all images.
    """
    def __init__(self,name, widget,
                 z_index=None,
                 border=[0, 0], offset=[0, 0],
                 imgs={},
                 default=None,
                 frame=[[2,10,2],[2,10,2]],
                 scale=(0, 0),
                 repeat_edge=False,
                 repeat_center=False,
                 tex_size=None,
                 ):
        super().__init__(name, widget, z_index, border, offset, imgs, default)

        if tex_size is None:
            t = list(imgs.values())[0]
            self.tsx, self.tsy = self.widget.peng.resourceMgr.getTexSize(*t)  # Texture Size in pixels
        else:
            self.tsx, self.tsy = tex_size
        self.frame_x = list(
            map(lambda x: x * (self.tsx / sum(frame[0])), frame[0]))  # Frame Size in the texture, in pixels
        self.frame_y = list(map(lambda y: y * (self.tsy / sum(frame[1])), frame[1]))

        self._scale = scale

        self.repeat_edge = repeat_edge
        self.repeat_center = repeat_center

        for i in frame:
            if (self.repeat_edge or self.repeat_center) and i[1] == 0:
                raise ValueError("Cannot repeat edges or center with the middle frame being 0")

    @property
    def scale(self):
        if self._scale == (None, None):
            raise ValueError(f"Scale cannot be {self._scale}")

        scale = self._scale
        if scale[0] == 0:  # 0 makes the resulting frames similar to the texture frames but scaled up to the widget size
            scale = self.size[0] / sum(self.frame_x), scale[1]
        if scale[1] == 0:
            scale = scale[0], self.size[1] / sum(self.frame_y)
        if scale[0] == None:  # None makes the scale similar to the second scale
            scale = scale[1], scale[1]
        if scale[1] == None:
            scale = scale[0], scale[0]
        return scale

    @property
    def size(self):
        return self.getSize()

    def initialize(self):
        self.cur_img = self.cur_img if self.cur_img is not None else (
            self.default_img if self.default_img is not None else list(self.imgs.keys())[0])

        if (self.frame_x[0] + self.frame_x[2]) * self.scale[0] > self.widget.size[0] or \
                (self.frame_y[0] + self.frame_y[2]) * self.scale[1] > self.widget.size[1]:
            raise ValueError(f"Scale {self.scale} is too large for this widget")

        self.bg_group = _DynImageGroup(self, self.group)
        self.vlist_corners = self.widget.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_edges = self.widget.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_center = self.widget.submenu.batch2d.add(4, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.regVList(self.vlist_corners)
        self.regVList(self.vlist_edges)
        self.regVList(self.vlist_center)

    def on_redraw(self):
        WidgetLayer.on_redraw(self)

        # Convenience Variables
        sx, sy = self.size
        x, y, _, _ = self.getPos()

        # Frame length in the result, in pixels
        flx, fcx, frx = map(lambda x: self.scale[0] * x, self.frame_x)
        sfcx = sx - (flx + frx)  # Stretched center frame length
        fdy, fcy, fuy = map(lambda y: self.scale[1] * y, self.frame_y)
        sfcy = sy - (fdy + fuy)

        amx, amy, rx, ry = 0, 0, 0, 0
        if self.repeat_center or self.repeat_edge:
            amx, amy = int(sfcx / fcx), int(sfcy / fcy)  # Amount of complete textures in an edge
            rx, ry = sfcx % fcx, sfcy % fcy  # Length of the rest tile in pixels

        # Vertices

        # 11-10---15-14
        # |   |   |   |
        # 8---9---12-13
        # |   |   |   |
        # 3---2---7---6
        # |   |   |   |
        # 0---1---4---5

        # Corners
        #     x         y
        v0 = x, y
        v1 = x + flx, y
        v2 = x + flx, y + fdy
        v3 = x, y + fdy

        v4 = x + sx - frx, y
        v5 = x + sx, y
        v6 = x + sx, y + fdy
        v7 = x + sx - frx, y + fdy

        v8 = x, y + sy - fuy
        v9 = x + flx, y + sy - fuy
        v10 = x + flx, y + sy
        v11 = x, y + sy

        v12 = x + sx - frx, y + sy - fuy
        v13 = x + sx, y + sy - fuy
        v14 = x + sx, y + sy
        v15 = x + sx - frx, y + sy

        self.vlist_corners.vertices = (
                v0 + v1 + v2 + v3 +
                v4 + v5 + v6 + v7 +
                v8 + v9 + v10 + v11 +
                v12 + v13 + v14 + v15
        )

        if self.repeat_edge:
            self.vlist_edges.resize(8 * (amx + amy + 2))

            vd, vu, vl, vr = [], [], [], []
            for i in range(amx):
                vd += x + flx + i * fcx, y
                vd += x + flx + (i + 1) * fcx, y
                vd += x + flx + (i + 1) * fcx, y + fdy
                vd += x + flx + i * fcx, y + fdy

                vu += x + flx + i * fcx, y + sy - fuy
                vu += x + flx + (i + 1) * fcx, y + sy - fuy
                vu += x + flx + (i + 1) * fcx, y + sy
                vu += x + flx + i * fcx, y + sy

            vd += x + sx - frx - rx, y
            vd += x + sx - frx, y
            vd += x + sx - frx, y + fdy
            vd += x + sx - frx - rx, y + fdy

            vu += x + sx - frx - rx, y + sy - fuy
            vu += x + sx - frx, y + sy - fuy
            vu += x + sx - frx, y + sy
            vu += x + sx - frx - rx, y + sy

            for j in range(amy):
                vl += x, y + fdy + j * fcy
                vl += x + flx, y + fdy + j * fcy
                vl += x + flx, y + fdy + (j + 1) * fcy
                vl += x, y + fdy + (j + 1) * fcy

                vr += x + sx - frx, y + fdy + j * fcy
                vr += x + sx, y + fdy + j * fcy
                vr += x + sx, y + fdy + (j + 1) * fcy
                vr += x + sx - frx, y + fdy + (j + 1) * fcy

            vl += x, y + sy - fuy - ry
            vl += x + flx, y + sy - fuy - ry
            vl += x + flx, y + sy - fuy
            vl += x, y + sy - fuy

            vr += x + sx - frx, y + sy - fuy - ry
            vr += x + sx, y + sy - fuy - ry
            vr += x + sx, y + sy - fuy
            vr += x + sx - frx, y + sy - fuy

            self.vlist_edges.vertices = vd + vl + vr + vu
        else:
            self.vlist_edges.vertices = (
                    v1 + v4 + v7 + v2 +
                    v3 + v2 + v9 + v8 +
                    v7 + v6 + v13 + v12 +
                    v9 + v12 + v15 + v10
            )

        if self.repeat_center:
            self.vlist_center.resize(4 * (amx + 1) * (amy + 1))
            v = []

            # Completed tiles
            for j in range(amy):
                for i in range(amx):
                    v += x + flx + i * fcx, y + fdy + j * fcy
                    v += x + flx + (i + 1) * fcx, y + fdy + j * fcy
                    v += x + flx + (i + 1) * fcx, y + fdy + (j + 1) * fcy
                    v += x + flx + i * fcx, y + fdy + (j + 1) * fcy

            # X-shortened tiles
            for j in range(amy):
                v += x + sx - frx - rx, y + fdy + j * fcy
                v += x + sx - frx, y + fdy + j * fcy
                v += x + sx - frx, y + fdy + (j + 1) * fcy
                v += x + sx - frx - rx, y + fdy + (j + 1) * fcy

            # Y-shortened tiles
            for i in range(amx):
                v += x + flx + i * fcx, y + sy - fuy - ry
                v += x + flx + (i + 1) * fcx, y + sy - fuy - ry
                v += x + flx + (i + 1) * fcx, y + sy - fuy
                v += x + flx + i * fcx, y + sy - fuy

            # X-Y-shortened tile
            v += x + sx - frx - rx, y + sy - fuy - ry
            v += x + sx - frx, y + sy - fuy - ry
            v += x + sx - frx, y + sy - fuy
            v += x + sx - frx - rx, y + sy - fuy

            self.vlist_center.vertices = v
        else:
            self.vlist_center.vertices = v2 + v7 + v12 + v9

        t = self.transform_texture(self.imgs[self.cur_img], amx, amy, rx, ry)
        self.vlist_corners.tex_coords, self.vlist_edges.tex_coords, self.vlist_center.tex_coords = t

    def transform_texture(self, texture, amx, amy, rx, ry):
        t = texture[2]
        sx, sy = self.size

        tx, ty = t[3] - t[0], t[10] - t[1]  # Texture Size on texture level

        # Frame length on texture level
        flx, fcx, frx = map(lambda x: x * tx / self.tsx, self.frame_x)
        fdy, fcy, fuy = map(lambda y: y * ty / self.tsy, self.frame_y)

        if self.repeat_center or self.repeat_edge:
            rx = (rx * tx) / (self.tsx * self.scale[0])
            ry *= ty / self.tsy / self.scale[1]

        t0 = t[0], t[1], t[2]
        t1 = t[0] + flx, t[1], t[2]
        t2 = t[0] + flx, t[1] + fdy, t[2]
        t3 = t[0], t[1] + fdy, t[2]

        t4 = t[3] - frx, t[4], t[5]
        t5 = t[3], t[4], t[5]
        t6 = t[3], t[4] + fdy, t[5]
        t7 = t[3] - frx, t[4] + fdy, t[5]

        t8 = t[9], t[10] - fuy, t[11]
        t9 = t[9] + flx, t[10] - fuy, t[11]
        t10 = t[9] + flx, t[10], t[11]
        t11 = t[9], t[10], t[11]

        t12 = t[6] - frx, t[7] - fuy, t[8]
        t13 = t[6], t[7] - fuy, t[8]
        t14 = t[6], t[7], t[8]
        t15 = t[6] - frx, t[7], t[8]

        corner_tex = t0 + t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9 + t10 + t11 + t12 + t13 + t14 + t15

        if self.repeat_edge:
            td, tl, tr, tu = [], [], [], []

            td += (t1 + t4 + t7 + t2) * amx
            tu += (t9 + t12 + t15 + t10) * amx

            td += t1
            td += t[0] + flx + rx, t[1], t[2]
            td += t[0] + flx + rx, t[1] + fdy, t[2]
            td += t2

            tu += t9
            tu += t[9] + flx + rx, t[10] - fuy, t[11]
            tu += t[9] + flx + rx, t[10], t[11]
            tu += t10

            tl += (t3 + t2 + t9 + t8) * amy
            tr += (t7 + t6 + t13 + t12) * amy

            tl += t3 + t2
            tl += t[0] + flx, t[1] + fdy + ry, t[2]
            tl += t[0], t[1] + fdy + ry, t[2]

            tr += t7 + t6
            tr += t[3], t[4] + fdy + ry, t[5]
            tr += t[3] - frx, t[4] + fdy + ry, t[5]

            edge_tex = td + tl + tr + tu
        else:
            edge_tex = t1 + t4 + t7 + t2 + t3 + t2 + t9 + t8 + t7 + t6 + t13 + t12 + t9 + t12 + t15 + t10

        if self.repeat_center:
            tc = []

            tc += (t2 + t7 + t12 + t9) * amx * amy
            for i in range(amy):
                tc += t2
                tc += t[0] + flx + rx, t[1] + fdy, t[2]
                tc += t[9] + flx + rx, t[10] - fuy, t[11]
                tc += t9

            for i in range(amx):
                tc += t2 + t7
                tc += t[3] - frx, t[4] + fdy + ry, t[5]
                tc += t[0] + flx, t[1] + fdy + ry, t[2]

            tc += t2
            tc += t[0] + flx + rx, t[1] + fdy, t[2]
            tc += t[0] + flx + rx, t[1] + fdy + ry, t[8]
            tc += t[0] + flx, t[1] + fdy + ry, t[2]

            center_tex = tc
        else:
            center_tex = t2 + t7 + t12 + t9

        return corner_tex, edge_tex, center_tex


class ImageButtonWidgetLayer(DynImageWidgetLayer):
    """
    Subclass of :py:class:`DynImageWidgetLayer()` that acts like an :py:class:`ImageButton()`\ .
    
    The ``img_*`` arguments are of the same format as in :py:class:`DynImageWidgetLayer()`\ .
    
    This class internally uses the :py:meth:`BasicWidget.getState()` method for getting the state of the widget.
    """
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                img_idle=None,img_pressed=None,img_hover=None,img_disabled=None,
                ):
        super(ImageButtonWidgetLayer,self).__init__(name,widget,z_index,border,
                    imgs={"idle":img_idle,
                          "pressed":img_pressed,
                          "hover":img_hover,
                          "disabled":img_disabled,
                          },
                    default="idle",
                    )
        self.widget.addAction("statechanged",lambda:self.switchImage(self.widget.getState()))


class LabelWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer()` displaying arbitrary plain text.
    
    Note that this method internally uses a pyglet Label that is centered on the Layer.
    
    The ``z_index`` for this Layer defaults to ``2``\ .
    """
    z_index = 2
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                label="",
                font_size=None,font=None,
                font_color=None,
                multiline=False,
                ):
        font = font if font is not None else widget.submenu.font
        font_size = font_size if font_size is not None else widget.submenu.font_size
        font_color = font_color if font_color is not None else widget.submenu.font_color
        super(LabelWidgetLayer,self).__init__(name,widget,z_index,border,offset)
        
        self._label = pyglet.text.Label(str(label),
                font_name=font,
                font_size=font_size,
                color=font_color,
                x=0,y=0,
                batch=self.widget.submenu.batch2d,
                group=self.group,
                anchor_x="center", anchor_y="center",
                width=self.getSize()[0],#height=self.getSize()[1],
                multiline=multiline,
                )
        if getattr(label,"_dynamic",False):
            def f():
                self.label = str(label)
            self.widget.peng.i18n.addAction("setlang",f)
        
        self.on_redraw()
    
    def on_redraw(self,dt=None):
        super(LabelWidgetLayer,self).on_redraw()
        self.redraw_label()
    def redraw_label(self):
        """
        Re-draws the text by calculating its position.
        
        Currently, the text will always be centered on the position of the layer.
        """
        # Convenience variables
        x,y,_,_ = self.getPos()
        sx,sy = self.getSize()
        
        self._label.x = x+sx/2.
        self._label.y = y+sy/2.
        self._label.width = sx
        # Height is not set, would look weird otherwise
        #self._label.height = sx
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
    
    @property
    def label(self):
        """
        Property for accessing the text of the label.
        """
        return self._label.text
    @label.setter
    def label(self,label):
        self._label.text = str(label)

class FormattedLabelWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer()` serving as a base class for other formatted label layers.
    
    The Label Type can be set via the class attribute ``cls``\ , it should be set to any class that is compatible with :py:class:`pyglet.text.Label`\ .
    
    It is recommended to use one of the subclasses of this class instead of this class directly.
    
    The ``z_index`` for this Layer defaults to ``2``\ .
    """
    z_index = 2
    cls = pyglet.text.HTMLLabel
    def __init__(self,name,widget,
                z_index=None,
                border=[0,0],offset=[0,0],
                label="",
                font_size=None,font="Arial",
                font_color=None,
                multiline=False,
                ):
        super(FormattedLabelWidgetLayer,self).__init__(name,widget,z_index,border,offset)
        
        self.font_size = font_size
        self.font_name = font
        self.font_color = font_color
        
        self._label = self.cls(str(label),
                x=0,y=0,
                batch=self.widget.submenu.batch2d,
                group=self.group,
                anchor_x="center", anchor_y="center",
                width=self.getSize()[0],#height=self.getSize()[1],
                multiline=multiline,
                )
        if getattr(label,"_dynamic",False):
            def f():
                self.label = str(label)
            self.peng.i18n.addAction("setlang",f)
        
        self.on_redraw()
    
    def on_redraw(self,dt=None):
        super(FormattedLabelWidgetLayer,self).on_redraw()
        self.redraw_label()
    def redraw_label(self):
        """
        Re-draws the text by calculating its position.
        
        Currently, the text will always be centered on the position of the layer.
        """
        # Convenience variables
        x,y,_,_ = self.getPos()
        sx,sy = self.getSize()
        
        if self.font_name is not None:
            self._label.font_name = self.font_name
        if self.font_size is not None:
            self._label.font_size = self.font_size
        if self.font_color is not None:
            self._label.color = self.font_color
        
        self._label.x = x+sx/2.
        self._label.y = y+sy/2.
        self._label.width = sx
        # Height is not set, would look weird otherwise
        #self._label.height = sx
        self._label._update() # Needed to prevent the label from drifting to the top-left after resizing by odd amounts
    
    @property
    def label(self):
        """
        Property for accessing the text of the label.
        
        Note that depending on the type of format, this property may not exactly represent the original text as it is converted internally.
        """
        return self._label.text
    @label.setter
    def label(self,label):
        self._label.text = label

class HTMLLabelWidgetLayer(FormattedLabelWidgetLayer):
    """
    Subclass of :py:class:`FormattedLabelWidgetLayer` implementing a basic HTML Label.
    
    Note that not all tags are supported, see the docs for :py:class:`pyglet.text.HTMLLabel` for details.
    """
    cls = pyglet.text.HTMLLabel

# TODO: support other formats (Markdown, Pyglet-style Attributed Text, Maybe others?)

class BaseBorderWidgetLayer(WidgetLayer):
    """
    Subclass of :py:class:`WidgetLayer` that displays a basic border around the layer.
    
    Note that not all styles will look good with this class, see :py:class:`ButtonBorderWidgetLayer()` for more information.
    
    Note that the ``border`` and ``offset`` arguments have been renamed to ``base_border`` and ``base_offset`` to prevent naming conflicts.
    
    Subclasses may set the :py:attr:`n_vertices` value to change the number of
    vertices or :py:attr:`change_on_press` to change the default value for the
    argument of the same name.
    By default, 36 vertices are used and ``changed_on_press`` is set to ``True``\ .
    
    The ``z_index`` for this Layer defaults to ``0.5``\ .
    """
    z_index = 0.5 # between default and image layer
    
    n_vertices = 36
    change_on_press = True
    
    color_bg = None
    color_o = None
    color_i = None
    color_s = None
    color_h = None
    
    def __init__(self,name,widget,
                z_index=None,
                base_border=[0,0],base_offset=[0,0],
                border=[4,4, 4,4, 4,4, 4,4],
                style="flat",
                batch=None, change_on_press=None,
                ):
        super(BaseBorderWidgetLayer,self).__init__(name,widget,z_index,base_border,base_offset)
        
        self.bborder = border
        self.style = style
        
        if style=="material" and self.__class__==BaseBorderWidgetLayer:
            warnings.warn("Material style may have visual artifacts if used with BaseBorderWidgetLayer, use ButtonBorderWidgetLayer instead",stacklevel=2)
        elif style=="gradient" and self.__class__==BaseBorderWidgetLayer:
            warnings.warn("Gradient style may have visual artifacts if used with BaseBorderWidgetLayer, use ButtonBorderWidgetLayer instead",stacklevel=2)
        elif style=="oldshadow" and self.__class__==BaseBorderWidgetLayer:
            warnings.warn("Oldshadow style may have visual artifacts if used with BaseBorderWidgetLayer, use ButtonBorderWidgetLayer instead",stacklevel=2)
        
        self.batch = batch
        
        self.change_on_press = change_on_press if change_on_press is not None else self.change_on_press
        
        self.styles = {}
        self.addStyle("flat",self.s_flat)
        self.addStyle("gradient",self.s_gradient)
        self.addStyle("oldshadow",self.s_oldshadow)
        self.addStyle("material",self.s_material)
    
    def addStyle(self,name,func):
        """
        Adds a style to the layer.
        
        Note that styles must be registered seperately for each layer.
        
        ``name`` is the (string) name of the style.
        
        ``func`` will be called with its arguments as ``(bg,o,i,s,h)``\ , see :py:meth:`getColors()` for more information.
        """
        self.styles[name]=func
    def getColors(self):
        """
        Overrideable function that generates the colors to be used by various styles.
        
        Should return a 5-tuple of ``(bg,o,i,s,h)``\ .
        
        ``bg`` is the base color of the background.
        
        ``o`` is the outer color, it is usually the same as the background color.
        
        ``i`` is the inner color, it is usually lighter than the background color.
        
        ``s`` is the shadow color, it is usually quite a bit darker than the background.
        
        ``h`` is the highlight color, it is usually quite a bit lighter than the background.
        
        The returned values may also be statically overridden by setting the :py:attr:`color_<var>` attribute to anything but ``None``\ .
        """
        
        bg = self.widget.submenu.bg[:3] if isinstance(self.widget.submenu.bg,list) or isinstance(self.widget.submenu.bg,tuple) else [242,241,240]
        bg = bg if self.color_bg is None else self.color_bg
        
        o,i = bg, [min(bg[0]+8,255),min(bg[1]+8,255),min(bg[2]+8,255)]
        s,h = [max(bg[0]-40,0),max(bg[1]-40,0),max(bg[2]-40,0)], [min(bg[0]+12,255),min(bg[1]+12,255),min(bg[2]+12,255)]
        
        o = o if self.color_o is None else self.color_o
        i = i if self.color_i is None else self.color_i
        s = s if self.color_s is None else self.color_s
        h = h if self.color_h is None else self.color_h
        
        # Outer,Inner,Shadow,Highlight
        return bg,o,i,s,h
    
    def initialize(self):
        self.batch = self.batch if self.batch is not None else self.widget.submenu.batch2d
        
        self.vlist = self.batch.add(self.n_vertices,GL_QUADS,self.group,
            "v2f",
            "c3B",
            )
        self.regVList(self.vlist)
    initialize.__noautodoc__ = True
    def on_redraw(self):
        super(BaseBorderWidgetLayer,self).on_redraw()
        self.vlist.vertices = self.genVertices()
        
        if self.style not in self.styles:
            raise ValueError("Invalid Style")
        c = self.styles[self.style](*self.getColors())
        
        if len(c)==self.n_vertices*3: # one color per vertex
            # No need to change anything
            pass
        elif len(c)==20*3: # old button-style coloring
            c = self.stretchColors(c)
        else:
            raise ValueError("Style produced %s colors, but %s required"%(len(c)/3,self.n_vertices))
        
        self.vlist.colors = c
    def genVertices(self):
        """
        Called to generate the vertices used by this layer.
        
        The length of the output of this method should be three times the :py:attr:`n_vertices` attribute.
        
        See the source code of this method for more information about the order of the vertices.
        """
        sx,sy,ex,ey = self.getPos()
        b = self.bborder
        
        # Vertex Naming
        # Y
        # |1  2  3  4
        # |5  6  7  8
        # |9  10 11 12
        # |13 14 15 16
        # +------> X
        # Border order
        # 4 2-tuples
        # Each marks x,y offset from the respective corner
        # tuples are in order topleft,topright,bottomleft,bottomright
        # indices:
        # 0,1:topleft; 2,3:topright; 4,5:bottomleft; 6,7:bottomright
        # For a simple border that is even, just repeat the first tuple three more times
        
        v1 = sx,            ey
        v2 = sx+b[0],       ey
        v3 = ex-b[2],       ey
        v4 = ex,            ey
        
        v5 = sx,            ey-b[1]
        v6 = sx+b[0],       ey-b[1]
        v7 = ex-b[2],       ey-b[3]
        v8 = ex,            ey-b[3]
        
        v9 = sx,            sy+b[5]
        v10= sx+b[4],       sy+b[5]
        v11= ex-b[6],       sy+b[7]
        v12= ex,            sy+b[7]
        
        v13= sx,            sy
        v14= sx+b[4],       sy
        v15= ex-b[6],       sy
        v16= ex,            sy
        
        # Layer is separated into 9 sections, naming:
        # 1 2 3
        # 4 5 6
        # 7 8 9
        # Within each section, vertices are given counter-clockwise, starting with the bottom-left
        # 4 3
        # 1 2
        # This is important when assigning colors
        
        q1 = v5 +v6 +v2 +v1
        q2 = v6 +v7 +v3 +v2
        q3 = v7 +v8 +v4 +v3
        q4 = v9 +v10+v6 +v5
        q5 = v10+v11+v7 +v6
        q6 = v11+v12+v8 +v7
        q7 = v13+v14+v10+v9
        q8 = v14+v15+v11+v10
        q9 = v15+v16+v12+v11
        
        return q1+q2+q3+q4+q5+q6+q7+q8+q9
    def stretchColors(self,c):
        """
        Method that is called to stretch the colors.
        
        Note that this should be implemented by subclasses if plausible and reasonable.
        """
        # Subclasses should override this method to implement color stretching
        # Not possible here since the corners are implemented differently
        raise NotImplementedError("Color stretching is not supported on %s"%self.__class__.__name__)
    
    @property
    def pressed(self):
        """
        Read-only helper property to be used by styles for determining if the layer should be rendered as pressed or not.
        
        Note that this property may not represent the actual pressed state, it will always be False if ``change_on_press`` is disabled.
        """
        return self.change_on_press and self.widget.pressed
    @property
    def is_hovering(self):
        """
        Read-only helper property to be used by styles for determining if the layer should be rendered as hovered or not.
        
        Note that this property may not represent the actual hovering state, it will always be False if ``change_on_press`` is disabled.
        """
        return self.change_on_press and self.widget.is_hovering
    
    def s_flat(self,bg,o,i,s,h):
        # Flat style makes no difference between normal,hover and pressed
        return i*36
    s_flat.__noautodoc__ = True
    def s_gradient(self,bg,o,i,s,h):
        if self.pressed:
            i = s
        elif self.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
        
        return (
            o+i+o+o+
            i+i+o+o+
            i+o+o+o+
            o+i+i+o+
            i+i+i+i+
            i+o+o+i+
            o+o+i+o+
            o+o+i+i+
            o+o+o+i
            )
    s_gradient.__noautodoc__ = True
    def s_oldshadow(self,bg,o,i,s,h):
        if self.pressed:
            i = s
            s,h = h,s
        elif self.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
        
        return (
            h+h+h+h+
            h+h+h+h+
            h+s+h+h+
            h+h+h+h+
            i+i+i+i+
            s+s+s+s+
            h+s+h+h+
            s+s+s+s+
            s+s+s+s
            )
    s_oldshadow.__noautodoc__ = True
    def s_material(self,bg,o,i,s,h):
        if self.pressed:
            i = [max(bg[0]-20,0),max(bg[1]-20,0),max(bg[2]-20,0)]
        elif self.is_hovering:
            i = [max(bg[0]-10,0),max(bg[1]-10,0),max(bg[2]-10,0)]
        
        return (
            o+s+o+o+
            s+s+o+o+
            s+o+o+o+
            o+s+s+o+
            i+i+i+i+
            s+o+o+s+
            o+o+s+o+
            o+o+s+s+
            o+o+o+s
            )
    s_material.__noautodoc__ = True

class ButtonBorderWidgetLayer(BaseBorderWidgetLayer):
    """
    Subclass of :py:class:`BaseBorderWidgetLayer()` implementing Button-Style borders.
    
    This class is based on the :py:class:`ButtonBackground` class.
    This means that most styles are also available here and should look identical.
    
    Note that this class uses only 20 vertices and is thus not compatible with styles
    created for use with :py:class:`BaseBorderWidgetLayer`\ .
    
    Also note that the ``border`` argument also only receives two values instead of eight.
    """
    n_vertices = 20
    def __init__(self,name,widget,
                z_index=None,
                base_border=[0,0],base_offset=[0,0],
                border=[4,4],
                style="flat",
                batch=None, change_on_press=None,
                ):
        super(ButtonBorderWidgetLayer,self).__init__(name,widget,z_index,base_border,base_offset,border[0:2],style,batch,change_on_press)
    def genVertices(self):
        sx,sy, ex,ey = self.getPos()
        bx,by = self.bborder
        
        # Vertex Naming
        # Y
        # | 1       2
        # |  5     6
        # |  7     8
        # | 3       4
        # +-------> X
        # Quad order
        #    1
        # 4  5  2
        #    3
        # Within each quad, vertices are ordered from the bottom-left counter-clockwise
        
        v1 = sx,        ey
        v2 = ex,        ey
        v3 = sx,        sy
        v4 = ex,        sy
        
        v5 = sx+bx,     ey-by
        v6 = ex-bx,     ey-by
        v7 = sx+bx,     sy+by
        v8 = ex-bx,     sy+by
        
        q1 = v5+v6+v2+v1
        q2 = v8+v4+v2+v6
        q3 = v3+v4+v8+v7
        q4 = v3+v7+v5+v1
        q5 = v7+v8+v6+v5
        
        return q1+q2+q3+q4+q5
    genVertices.__noautodoc__ = True
    
    def s_flat(self,bg,o,i,s,h):
        # Flat style makes no difference between normal,hover and pressed
        cb1 = i+i+i+i
        cb2 = i+i+i+i
        cb3 = i+i+i+i
        cb4 = i+i+i+i
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    s_flat.__noautodoc__ = True
    def s_gradient(self,bg,o,i,s,h):
        if self.pressed:
            i = s
        elif self.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
        cb1 = i+i+o+o
        cb2 = i+o+o+i
        cb3 = o+o+i+i
        cb4 = o+i+i+o
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    s_gradient.__noautodoc__ = True
    def s_oldshadow(self,bg,o,i,s,h):
        if self.pressed:
            i = s
            s,h = h,s
        elif self.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
        cb1 = h+h+h+h
        cb2 = s+s+s+s
        cb3 = s+s+s+s
        cb4 = h+h+h+h
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    s_oldshadow.__noautodoc__ = True
    def s_material(self,bg,o,i,s,h):
        if self.pressed:
            i = [max(bg[0]-20,0),max(bg[1]-20,0),max(bg[2]-20,0)]
        elif self.is_hovering:
            i = [max(bg[0]-10,0),max(bg[1]-10,0),max(bg[2]-10,0)]
        cb1 = s+s+o+o
        cb2 = s+o+o+s
        cb3 = o+o+s+s
        cb4 = o+s+s+o
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
    s_material.__noautodoc__ = True
    
    def stretchColors(self,c):
        return c
    stretchColors.__noautodoc__ = True
