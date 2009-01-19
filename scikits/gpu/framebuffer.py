"""Framebuffer object.

This module is based on code which is

Copyright (c) 2009, Richard Jones

and is released under the MIT license.  See LICENSE.txt for more detail.

"""

__all__ = ['Framebuffer']

from pyglet import gl, image
import ctypes

from scikits.gpu.config import require_extension, MAX_COLOR_ATTACHMENTS
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

    def __init__(self):
        """Framebuffer Object (FBO) for off-screen rendering.

        A framebuffer object contains one or more
        framebuffer-attachable images.  These can be either
        renderbuffers or texture images.

        For now the framebuffer object handles only textures.

        """
        ## Create a framebuffer object
        framebuffer = gl.GLuint()
        gl.glGenFramebuffersEXT(1, ctypes.byref(framebuffer))
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, framebuffer)

        self.id = framebuffer
        self.MAX_COLOR_ATTACHMENTS = MAX_COLOR_ATTACHMENTS

        self._textures = []

    def add_texture(self, shape, dtype=gl.GL_UNSIGNED_BYTE):
        """Add texture image to the framebuffer object.

        Parameters
        ----------
        shape : tuple of ints
            Dimension of framebuffer.  Note that for earlier versions
            of OpenGL, height and width dimensions must be a power of
            two.  Valid shapes include (16,), (16, 17), (16, 16, 3).
        dtype : opengl data-type, e.g. GL_FLOAT, GL_UNSIGNED_BYTE

        Returns
        -------
        slot : int
            The slot number to which the texture was bound.  E.g., in the
            case of GL_COLOR_ATTACHMENT3_EXT, returns 3.

        """
        if len(self._textures) >= MAX_COLOR_ATTACHMENTS:
            raise RuntimeError("Maximum number of textures reached.  This "
                               "platform supports %d attachments." % \
                               MAX_COLOR_ATTACHMENTS)

        slot = getattr(gl, "GL_COLOR_ATTACHMENT%d_EXT" % len(self._textures))

        width, height, bands = _shape_to_3d(shape)

        if bands > 4:
            raise ValueError("Texture cannot have more than 4 colour layers.")

        colour_bands = {1: gl.GL_LUMINANCE,
                        2: gl.GL_LUMINANCE_ALPHA,
                        3: gl.GL_RGB,
                        4: gl.GL_RGBA}

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

        self._textures.append(tex)
        return len(self._textures) - 1

    def bind(self):
        """Set the FBO as the active rendering buffer.

        """
        if self.id:
            gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, self.id)
        else:
            raise RuntimeError("Cannot bind to deleted framebuffer.")

    def unbind(self):
        """Set the window as the active rendering buffer.

        """
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    def __del__(self):
        """Delete the framebuffer from the graphics card's memory.

        """
        self.unbind()
        if self.id:
            gl.glDeleteFramebuffersEXT(1, self.id)
            self.id = None
