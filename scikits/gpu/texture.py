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

from pyglet.image import AbstractImage
from pyglet import gl
from pyglet.gl import *

# Need this so that current_context is exposed
from pyglet.window import *

from scikits.gpu.ntypes import memory_type

import math

def _nearest_pow2(x):
    return 2 ** int(round(math.log(x, 2)))

class Texture(AbstractImage):
    '''An image loaded into video memory that can be efficiently drawn
    to the framebuffer.

    Typically you will get an instance of Texture by accessing the `texture`
    member of any other AbstractImage.

    :Ivariables:
        `region_class` : class (subclass of TextureRegion)
            Class to use when constructing regions of this texture.
        `tex_coords` : tuple
            12-tuple of float, named (u1, v1, r1, u2, v2, r2, ...).  u, v, r
            give the 3D texture coordinates for vertices 1-4.  The vertices
            are specified in the order bottom-left, bottom-right, top-right
            and top-left.
        `target` : int
            The GL texture target (e.g., ``GL_TEXTURE_2D``).
        `level` : int
            The mipmap level of this texture.

    '''

    region_class = None # Set to TextureRegion after it's defined
    tex_coords = (0., 0., 0., 1., 0., 0., 1., 1., 0., 0., 1., 0.)
    tex_coords_order = (0, 1, 2, 3)
    level = 0
    images = 1
    x = y = z = 0

    def __init__(self, width, height, target, id):
        super(Texture, self).__init__(width, height)
        self.target = target
        self.id = id
        self._context = gl.current_context

    def delete(self):
        '''Delete the texture from video memory.

        :deprecated: Textures are automatically released during object
            finalization.
        '''
        warnings.warn(
            'Texture.delete() is deprecated; textures are '
            'released through GC now')
        self._context.delete_texture(self.id)
        self.id = 0

    def __del__(self):
        try:
            self._context.delete_texture(self.id)
        except:
            pass

    @classmethod
    def create(cls, width, height,
               format=GL_RGBA, dtype=GL_UNSIGNED_BYTE, internalformat=GL_RGBA,
               rectangle=False, force_rectangle=False):
        '''Create an empty Texture.

        If `rectangle` is ``False`` or the appropriate driver extensions are
        not available, a larger texture than requested will be created, and
        a `TextureRegion` corresponding to the requested size will be
        returned.

        :Parameters:
            `width` : int
                Width of the texture.
            `height` : int
                Height of the texture.
            `format` : int
                Format of the texture image data.  One of
                ``GL_COLOR_INDEX``, ``GL_DEPTH_COMPONENT``, ``GL_RGB``,
                ``GL_RGBA``, ``GL_RED``, ``GL_GREEN``, ``GL_BLUE``,
                ``GL_ALPHA``, ``GL_LUMINANCE``, or ``GL_LUMINANCE_ALPHA``.
            `dtype` : int
                GL constant describing the underlying data-type of the
                texture, e.g. ``GL_UNSIGNED_BYTE`` or ``GL_FLOAT``.
            `internalformat` : int
                GL constant giving the internal bit-format of the
                texture; for example, ``GL_R3_G3_B2``.  This is a
                recommendation to OpenGL, but will not necessarily be
                followed.
            `rectangle` : bool
                ``True`` if a rectangular texture is permitted.  See
                `AbstractImage.get_texture`.
            `force_rectangle` : bool
                ``True`` if a rectangular texture is required.  See
                `AbstractImage.get_texture`.

                **Since:** pyglet 1.2.

        :rtype: `Texture`

        :since: pyglet 1.1
        '''
        target = GL_TEXTURE_2D
        if rectangle or force_rectangle:
            if not force_rectangle and _is_pow2(width) and _is_pow2(height):
                rectangle = False
            elif gl_info.have_extension('GL_ARB_texture_rectangle'):
                target = GL_TEXTURE_RECTANGLE_ARB
                rectangle = True
            elif gl_info.have_extension('GL_NV_texture_rectangle'):
                target = GL_TEXTURE_RECTANGLE_NV
                rectangle = True
            else:
                rectangle = False

        if force_rectangle and not rectangle:
            raise ImageException('Texture rectangle extensions not available')

        if rectangle:
            texture_width = width
            texture_height = height
        else:
            texture_width = _nearest_pow2(width)
            texture_height = _nearest_pow2(height)

        id = GLuint()
        glGenTextures(1, byref(id))
        glBindTexture(target, id.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

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
                 (texture_width * texture_height * colour_bands[format]))()
        glTexImage2D(target, 0,
                     internalformat,
                     texture_width, texture_height,
                     0,
                     format, dtype,
                     blank)

        texture = cls(texture_width, texture_height, target, id.value)
        if rectangle:
            texture._is_rectangle = True
            texture.tex_coords = (0., 0., 0.,
                                  width, 0., 0.,
                                  width, height, 0.,
                                  0., height, 0.)

        glFlush()

        if texture_width == width and texture_height == height:
            return texture

        return texture.get_region(0, 0, width, height)

    @classmethod
    def create_for_size(cls, target, min_width, min_height,
                        internalformat=None):
        '''Create a Texture with dimensions at least min_width, min_height.
        On return, the texture will be bound.

        :Parameters:
            `target` : int
                GL constant giving texture target to use, typically
                ``GL_TEXTURE_2D``.
            `min_width` : int
                Minimum width of texture (may be increased to create a power
                of 2).
            `min_height` : int
                Minimum height of texture (may be increased to create a power
                of 2).
            `internalformat` : int
                GL constant giving internal format of texture; for example,
                ``GL_RGBA``.  If unspecified, the texture will not be
                initialised (only the texture name will be created on the
                instance).   If specified, the image will be initialised
                to this format with zero'd data.

        :rtype: `Texture`
        '''
        if target not in (GL_TEXTURE_RECTANGLE_NV, GL_TEXTURE_RECTANGLE_ARB):
            width = _nearest_pow2(min_width)
            height = _nearest_pow2(min_height)
            tex_coords = cls.tex_coords
        else:
            width = min_width
            height = min_height
            tex_coords = (0., 0., 0.,
                          width, 0., 0.,
                          width, height, 0.,
                          0., height, 0.)
        id = GLuint()
        glGenTextures(1, byref(id))
        glBindTexture(target, id.value)
        glTexParameteri(target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        if internalformat is not None:
            blank = (GLubyte * (width * height * 4))()
            glTexImage2D(target, 0,
                         internalformat,
                         width, height,
                         0,
                         GL_RGBA, GL_UNSIGNED_BYTE,
                         blank)
            glFlush()

        texture = cls(width, height, target, id.value)
        texture.tex_coords = tex_coords
        return texture

    def get_image_data(self, z=0):
        '''Get the image data of this texture.

        Changes to the returned instance will not be reflected in this
        texture.

        :Parameters:
            `z` : int
                For 3D textures, the image slice to retrieve.

        :rtype: `ImageData`
        '''
        glBindTexture(self.target, self.id)

        # Always extract complete RGBA data.  Could check internalformat
        # to only extract used channels. XXX
        format = 'RGBA'
        gl_format = GL_RGBA

        glPushClientAttrib(GL_CLIENT_PIXEL_STORE_BIT)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        buffer = \
            (GLubyte * (self.width * self.height * self.images * len(format)))()
        glGetTexImage(self.target, self.level,
                      gl_format, GL_UNSIGNED_BYTE, buffer)
        glPopClientAttrib()

        data = ImageData(self.width, self.height, format, buffer)
        if self.images > 1:
            data = data.get_region(0, z * self.height, self.width, self.height)
        return data

    image_data = property(lambda self: self.get_image_data(),
        doc='''An ImageData view of this texture.

        Changes to the returned instance will not be reflected in this
        texture.  If the texture is a 3D texture, the first image will be
        returned.  See also `get_image_data`.  Read-only.

        :deprecated: Use `get_image_data`.

        :type: `ImageData`
        ''')

    def get_texture(self, rectangle=False, force_rectangle=False):
        if force_rectangle and not self._is_rectangle:
            raise ImageException('Texture is not a rectangle.')
        return self

    # no implementation of blit_to_texture yet (could use aux buffer)

    def blit(self, x, y, z=0, width=None, height=None):
        t = self.tex_coords
        x1 = x - self.anchor_x
        y1 = y - self.anchor_y
        x2 = x1 + (width is None and self.width or width)
        y2 = y1 + (height is None and self.height or height)
        array = (GLfloat * 32)(
             t[0],  t[1],  t[2],  1.,
             x1,    y1,    z,     1.,
             t[3],  t[4],  t[5],  1.,
             x2,    y1,    z,     1.,
             t[6],  t[7],  t[8],  1.,
             x2,    y2,    z,     1.,
             t[9],  t[10], t[11], 1.,
             x1,    y2,    z,     1.)

        glPushAttrib(GL_ENABLE_BIT)
        glEnable(self.target)
        glBindTexture(self.target, self.id)
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glInterleavedArrays(GL_T4F_V4F, 0, array)
        glDrawArrays(GL_QUADS, 0, 4)
        glPopClientAttrib()
        glPopAttrib()

    def blit_into(self, source, x, y, z):
        glBindTexture(self.target, self.id)
        source.blit_to_texture(self.target, self.level, x, y, z)

    def get_region(self, x, y, width, height):
        return self.region_class(x, y, 0, width, height, self)

    def get_transform(self, flip_x=False, flip_y=False, rotate=0):
        '''Create a copy of this image applying a simple transformation.

        The transformation is applied to the texture coordinates only;
        `get_image_data` will return the untransformed data.  The
        transformation is applied around the anchor point.

        :Parameters:
            `flip_x` : bool
                If True, the returned image will be flipped horizontally.
            `flip_y` : bool
                If True, the returned image will be flipped vertically.
            `rotate` : int
                Degrees of clockwise rotation of the returned image.  Only
                90-degree increments are supported.

        :rtype: `TextureRegion`
        '''
        transform = self.get_region(0, 0, self.width, self.height)
        bl, br, tr, tl = 0, 1, 2, 3
        transform.anchor_x = self.anchor_x
        transform.anchor_y = self.anchor_y
        if flip_x:
            bl, br, tl, tr = br, bl, tr, tl
            transform.anchor_x = self.width - self.anchor_x
        if flip_y:
            bl, br, tl, tr = tl, tr, bl, br
            transform.anchor_y = self.height - self.anchor_y
        rotate %= 360
        if rotate < 0:
            rotate += 360
        if rotate == 0:
            pass
        elif rotate == 90:
            bl, br, tr, tl = br, tr, tl, bl
            transform.anchor_x, transform.anchor_y = \
                transform.anchor_y, \
                transform.width - transform.anchor_x
        elif rotate == 180:
            bl, br, tr, tl = tr, tl, bl, br
            transform.anchor_x = transform.width - transform.anchor_x
            transform.anchor_y = transform.height - transform.anchor_y
        elif rotate == 270:
            bl, br, tr, tl = tl, bl, br, tr
            transform.anchor_x, transform.anchor_y = \
                transform.height - transform.anchor_y, \
                transform.anchor_x
        else:
            assert False, 'Only 90 degree rotations are supported.'
        if rotate in (90, 270):
            transform.width, transform.height = \
                transform.height, transform.width
        transform._set_tex_coords_order(bl, br, tr, tl)
        return transform

    def _set_tex_coords_order(self, bl, br, tr, tl):
        tex_coords = (self.tex_coords[:3],
                      self.tex_coords[3:6],
                      self.tex_coords[6:9],
                      self.tex_coords[9:])
        self.tex_coords = \
            tex_coords[bl] + tex_coords[br] + tex_coords[tr] + tex_coords[tl]

        order = self.tex_coords_order
        self.tex_coords_order = \
            (order[bl], order[br], order[tr], order[tl])
