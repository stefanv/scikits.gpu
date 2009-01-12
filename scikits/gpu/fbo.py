"""Framebuffer object.

This module is based on code which is

Copyright (c) 2009, Richard Jones

and is released under the MIT license.  See LICENSE.txt for more detail.

"""

from pyglet import gl, image
import ctypes

from scikits.gpu.config import require_extension
from scikits.gpu.texture import Texture

class Framebuffer(object):
    require_extension('GL_EXT_framebuffer_object')

    def __init__(self, width, height, bands=3):
        """Framebuffer Object (FBO) for off-screen rendering.

        Parameters
        ----------
        width, height : int
            Dimension of framebuffer.  Note that for earlier versions
            of OpenGL, dimensions must be a power of two.
        bands : int
            Number of colour bands.
        dtype : numpy data-type, e.g. float, int, or
                opengl data-type, e.g. GL_FLOAT, GL_UNSIGNED_BYTE, or
                ctypes data-type, e.g. float, ubyte

        """
        colour_bands = {1: gl.GL_LUMINANCE,
                        2: gl.GL_LUMINANCE_ALPHA,
                        3: gl.GL_RGB,
                        4: gl.GL_RGBA}

        ## Create a framebuffer object

        # Number of framebuffer objects to allocate
        n = 1

        fbo_names = (n * gl.GLuint)()
        gl.glGenFramebuffersEXT(1, ctypes.cast(ctypes.byref(fbo_names),
                                               ctypes.POINTER(gl.GLuint)))

        # We only work with one from here on
        fbo = fbo_names[0]
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo)

        # allocate a texture and add to the frame buffer
        tex = Texture.create_for_size(gl.GL_TEXTURE_2D, width, height,
                                            colour_bands[bands])

        gl.glBindTexture(gl.GL_TEXTURE_2D, tex.id)
        gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT,
                                     gl.GL_COLOR_ATTACHMENT0_EXT,
                                     gl.GL_TEXTURE_2D, tex.id, 0)
        if (gl.glGetError() != gl.GL_NO_ERROR):
            raise RuntimeError("Could not create framebuffer texture.")

        status = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
        if not (status == gl.GL_FRAMEBUFFER_COMPLETE_EXT):
            raise RuntimeError("Could not set up framebuffer.")

    def bind(self):
        """Set the FBO as the active rendering buffer.

        """
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo)

    def unbind(self):
        """Set the window as the active rendering buffer.

        """
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    def delete(self):
        """Delete the framebuffer from the graphics card's memory.

        """
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
        gl.glDeleteFramebuffersEXT(1, ctypes.byref(fbo))
