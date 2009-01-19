"""Framebuffer object.

This module is based on code which is

Copyright (c) 2009, Richard Jones

and is released under the MIT license.  See LICENSE.txt for more detail.

"""

__all__ = ['Framebuffer']

from pyglet import gl, image
import ctypes

from scikits.gpu.config import require_extension
from scikits.gpu.texture import Texture

def _shape_to_3d(shape):
    """Return a shape with 3-dimensions, even if lower dimensional
    shape is provided.

    >>> _shape_to_3d([5])
    [5, 1, 1]

    >>> _shape_to_3d([5, 2])
    [5, 2, 1]

    >>> _shape_to_3d([5, 3, 1])
    [5, 3, 1]

    >>> try:
    ...     _shape_to_3d([5, 3, 3, 1])
    ... except ValueError:
    ...     pass

    """
    shape = list(shape)
    L = len(shape)

    if L > 3:
        raise ValueError("Shape cannot be higher than 3-dimensional.")

    shape += [1,]*(3 - L)

    return shape

class Framebuffer(object):
    require_extension('GL_EXT_framebuffer_object')
    fbo_names = None

    def __init__(self, shape, dtype=gl.GL_UNSIGNED_BYTE):
        """Framebuffer Object (FBO) for off-screen rendering.

        A framebuffer object contains one or more framebuffer-attachable images.
        These can be either renderbuffers or texture images.

        For now the framebuffer object handles only one image, a
        renderbuffer.

        Parameters
        ----------
        width, height : int
            Dimension of framebuffer.  Note that for earlier versions
            of OpenGL, dimensions must be a power of two.
        bands : int
            Number of colour bands.
        dtype : opengl data-type, e.g. GL_FLOAT, GL_UNSIGNED_BYTE

        """
        width, height, bands = _shape_to_3d(shape)

        if bands > 4:
            raise ValueError("Texture cannot have more than 4 colour layers.")


        colour_bands = {1: gl.GL_LUMINANCE,
                        2: gl.GL_LUMINANCE_ALPHA,
                        3: gl.GL_RGB,
                        4: gl.GL_RGBA}

        ## Create a framebuffer object

        # Number of framebuffer objects to allocate
        n = 1

        fbo_names = (n * gl.GLuint)()
        gl.glGenFramebuffersEXT(1, fbo_names)

        # We only work with one from here on
        fbo = fbo_names[0]
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo)

        # allocate a texture and add to the frame buffer
        tex = Texture(width, height,
                      format=colour_bands[bands],
                      dtype=dtype
                      )

        gl.glBindTexture(tex.target, tex.id)
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT,
                                     gl.GL_COLOR_ATTACHMENT0_EXT,
                                     tex.target, tex.id, 0)
        if (gl.glGetError() != gl.GL_NO_ERROR):
            raise RuntimeError("Could not create framebuffer texture.")

        status = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
        if not (status == gl.GL_FRAMEBUFFER_COMPLETE_EXT):
            raise RuntimeError("Could not set up framebuffer.")

        self.texure = tex
        self.framebuffer = fbo
        self.framebuffer_obj_names = fbo_names

    def bind(self):
        """Set the FBO as the active rendering buffer.

        """
        if self.framebuffer_obj_names:
            gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.framebuffer)
        else:
            raise RuntimeError("Cannot bind to deleted framebuffer.")

    def unbind(self):
        """Set the window as the active rendering buffer.

        """
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    def delete(self):
        """Delete the framebuffer from the graphics card's memory.

        """
        self.unbind()
        if self.framebuffer_obj_names:
            gl.glDeleteFramebuffersEXT(1, self.framebuffer_obj_names)
            self.framebuffer_obj_names = None

    def __del__(self):
        self.delete()
