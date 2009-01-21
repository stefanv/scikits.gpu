"""
The texture class is based on code from Pyglet, which is

Copyright (c) 2006-2008 Alex Holkner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.
  * Neither the name of pyglet nor the names of its
    contributors may be used to endorse or promote products
    derived from this software without specific prior written
    permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

__all__ = ['Texture', 'texture_target']

from pyglet import gl
from pyglet.gl import *

# Need this so that current_context is exposed
from pyglet.window import *

from scikits.gpu.ntypes import memory_type

import math

def texture_target(height, width):
    """Returns the hardware-specific target to render textures to.  For
    non-power-of-two textures, an OpenGL extension is required.

    Parameters
    ----------
    x, y : int
        Dimensions of the texture to be rendered.

    """
    def power_of_two(n):
        f = math.log(n, 2)
        return f == math.floor(f)

    if power_of_two(height) and power_of_two(width):
        return gl.GL_TEXTURE_2D
    elif gl.gl_info.have_extension('GL_ARB_texture_rectangle'):
        return gl.GL_TEXTURE_RECTANGLE_ARB
    else:
        raise HardwareSupportError("Hardware does not support non-power-of-two"
                                   " textures.")

class Texture(object):
    '''An image loaded into video memory that can be efficiently drawn
    to the framebuffer.

    '''
    tex_coords = (0., 0., 0., 1., 0., 0., 1., 1., 0., 0., 1., 0.)

    def __init__(self, width, height,
                 format=GL_RGBA, dtype=GL_FLOAT, internalformat=GL_RGBA):
        '''Create an empty Texture.

        Parameters
        ----------
        width : int
            Width of the texture.
        height : int
            Height of the texture.
        format : int
            Format of the texture image data.  One of
            ``GL_COLOR_INDEX``, ``GL_DEPTH_COMPONENT``, ``GL_RGB``,
            ``GL_RGBA``, ``GL_RED``, ``GL_GREEN``, ``GL_BLUE``,
            ``GL_ALPHA``, ``GL_LUMINANCE``, or ``GL_LUMINANCE_ALPHA``.
        dtype : int
            GL constant describing the underlying data-type of the
            texture, e.g. ``GL_UNSIGNED_BYTE`` or ``GL_FLOAT``.
        internalformat : int
            GL constant giving the internal bit-format of the
            texture; for example, ``GL_R3_G3_B2``.  This is a
            recommendation to OpenGL, but will not necessarily be
            followed.

        '''
        target = texture_target(height, width)

        id = GLuint()
        glGenTextures(1, byref(id))
        glBindTexture(target, id.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        colour_bands = {GL_COLOR_INDEX: 1,
                        GL_DEPTH_COMPONENT: 1,
                        GL_RGB: 3,
                        GL_RGBA: 4,
                        GL_RED: 1,
                        GL_GREEN: 1,
                        GL_BLUE: 1,
                        GL_ALPHA: 1,
                        GL_LUMINANCE: 1,
                        GL_LUMINANCE_ALPHA: 2}

        blank = (memory_type(dtype) * \
                 (width * height * colour_bands[format]))()
        glTexImage2D(target, 0,
                     internalformat,
                     width, height,
                     0,
                     format, dtype,
                     blank)

        if texture_target != gl.GL_TEXTURE_2D:
            self.tex_coords = (0., 0.,  0.,
                               width, 0., 0.,
                               width, height, 0.,
                               height, 0., 0.)

        glFlush()

        self.target = target
        self.id = id
        self.height, self.width = height, width

    def __del__(self):
        try:
            self._context.delete_texture(self.id)
        except:
            pass
