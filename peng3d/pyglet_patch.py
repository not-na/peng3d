#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyglet_patch.py
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
"""
These patches are used to fix specific problems with pyglet.

Note that these are not likely to stay, since I will have to verify that they still work with every Pyglet Release.
"""

__all__ = ["patch_float2int"]

import sys
import ctypes

import pyglet
import pyglet.graphics
from pyglet.graphics.vertexbuffer import MappableVertexBufferObject
from pyglet.graphics import vertexbuffer

from pyglet.gl import *

### patch_float2int

def _get_region(self, buffer, start, count):
        '''Map a buffer region using this attribute as an accessor.

        The returned region can be modified as if the buffer was a contiguous
        array of this attribute (though it may actually be interleaved or
        otherwise non-contiguous).

        The returned region consists of a contiguous array of component
        data elements.  For example, if this attribute uses 3 floats per
        vertex, and the `count` parameter is 4, the number of floats mapped
        will be ``3 * 4 = 12``.

        :Parameters:
            `buffer` : `AbstractMappable`
                The buffer to map.
            `start` : int
                Offset of the first vertex to map.
            `count` : int
                Number of vertices to map

        :rtype: `AbstractBufferRegion`
        '''
        byte_start = self.stride * start
        byte_size = self.stride * count
        array_count = self.count * count
        if self.stride == self.size or not array_count:
            # non-interleaved
            ptr_type = ctypes.POINTER(self.c_type * array_count)
            return buffer.get_region(byte_start, byte_size, ptr_type)
        else:
            # interleaved
            byte_start += self.offset
            byte_size -= self.offset
            elem_stride = self.stride // ctypes.sizeof(self.c_type)
            elem_offset = self.offset // ctypes.sizeof(self.c_type)
            ptr_type = ctypes.POINTER(
                self.c_type * int((count * elem_stride - elem_offset)))
            region = buffer.get_region(byte_start, byte_size, ptr_type)
            return vertexbuffer.IndirectArrayRegion(
                region, array_count, self.count, elem_stride)

def _bind(self):
        # Commit pending data
        super(MappableVertexBufferObject, self).bind()
        size = self._dirty_max - self._dirty_min
        if size > 0:
            if size == self.size:
                glBufferData(self.target, self.size, self.data, self.usage)
            else:
                glBufferSubData(self.target, self._dirty_min, int(size),
                    self.data_ptr + self._dirty_min)
            self._dirty_min = sys.maxsize
            self._dirty_max = 0

def _iar__setitem__(self, index, value):
        count = self.count
        if not isinstance(index, slice):
            elem = index // count
            j = index % count
            self.region.array[elem * self.stride + j] = value
            return

        start = index.start or 0
        stop = index.stop
        step = index.step or 1
        if start < 0:
            start = self.size + start
        if stop is None:
            stop = self.size
        elif stop < 0:
            stop = self.size + stop

        assert step == 1 or step % count == 0, \
            'Step must be multiple of component count'

        data_start = (start // count) * self.stride + start % count
        data_stop = (stop // count) * self.stride + stop % count

        # ctypes does not support stepped slicing, so do the work in a list
        # and copy it back.
        data = self.region.array[:]
        if step == 1:
            data_step = self.stride
            value_step = count
            for i in range(count):
                data[data_start + i:int(data_stop) + i:data_step] = \
                    value[i::value_step]
        else:
            data_step = (step // count) * self.stride
            data[data_start:data_stop:data_step] = value
        self.region.array[:] = data

def _draw(self, mode, vertex_list=None):
        '''Draw vertices in the domain.

        If `vertex_list` is not specified, all vertices in the domain are
        drawn.  This is the most efficient way to render primitives.

        If `vertex_list` specifies a `VertexList`, only primitives in that
        list will be drawn.

        :Parameters:
            `mode` : int
                OpenGL drawing mode, e.g. ``GL_POINTS``, ``GL_LINES``, etc.
            `vertex_list` : `VertexList`
                Vertex list to draw, or ``None`` for all lists in this domain.

        '''
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        for buffer, attributes in self.buffer_attributes:
            buffer.bind()
            for attribute in attributes:
                attribute.enable()
                attribute.set_pointer(attribute.buffer.ptr)
        if vertexbuffer._workaround_vbo_finish:
            glFinish()

        if vertex_list is not None:
            glDrawArrays(mode, vertex_list.start, vertex_list.count)
        else:
            starts, sizes = self.allocator.get_allocated_regions()
            primcount = len(starts)
            if primcount == 0:
                pass
            elif primcount == 1:
                # Common case
                glDrawArrays(mode, starts[0], int(sizes[0]))
            elif gl_info.have_version(1, 4):
                starts = (GLint * primcount)(*starts)
                sizes = (GLsizei * primcount)(*sizes)
                glMultiDrawArrays(mode, starts, sizes, primcount)
            else:
                for start, size in zip(starts, sizes):
                    glDrawArrays(mode, start, size)

        for buffer, _ in self.buffer_attributes:
            buffer.unbind()
        glPopClientAttrib()

def patch_float2int():
    """
    Patches the :py:mod:`pyglet.graphics.vertexattribute`\ , :py:mod:`pyglet.graphics.vertexbuffer` and :py:mod:`pyglet.graphics.vertexdomain` modules.
    
    This patch is only needed with Python 3.x and will be applied automatically when initializing :py:class:`Peng()`\ .
    
    The patches consist of simply converting some list indices, slices and other numbers to integers from floats with .0. These patches have not been tested thoroughly, but work with at least test.py
    
    Can be enabled and disabled via :confval:`pyglet.patch.patch_float2int`\ .
    """
    pyglet.graphics.vertexattribute.AbstractAttribute.get_region = _get_region
    pyglet.graphics.vertexbuffer.MappableVertexBufferObject.bind = _bind
    pyglet.graphics.vertexbuffer.IndirectArrayRegion.__setitem__ = _iar__setitem__
    pyglet.graphics.vertexdomain.VertexDomain.draw = _draw

### End patch_float2int
