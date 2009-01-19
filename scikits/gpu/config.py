__all__ = ['HardwareSupportError', 'GLSLError', 'MAX_COLOR_ATTACHMENTS',
           'require_extension', 'hardware_info', 'texture_target']

from pyglet import gl
import pyglet.gl.gl_info as gli
import ctypes

MAX_COLOR_ATTACHMENTS = gl.GLint()
gl.glGetIntegerv(gl.GL_MAX_COLOR_ATTACHMENTS,
                 ctypes.byref(MAX_COLOR_ATTACHMENTS))
MAX_COLOR_ATTACHMENTS = MAX_COLOR_ATTACHMENTS.value

class HardwareSupportError(Exception):
    def __init__(self, message):
        self.message = "Your graphics hardware does not support %s." % \
                       message

    def __str__(self):
        return self.message

class GLSLError(Exception):
    pass

def require_extension(ext):
    """Ensure that the given graphics extension is supported.

    """
    if not gl.gl_info.have_extension(ext):
        raise HardwareSupportError("the %s extension" % ext)

def hardware_info():
    info = {'vendor': gli.get_vendor(),
            'renderer': gli.get_renderer(),
            'version': gli.get_version()}
    return info

def texture_target(height, width):
    """Returns the hardware-specific target to render textures to.  For
    non-power-of-two textures, an OpenGL extension is required.

    Parameters
    ----------
    x, y : int
        Dimensions of the texture to be rendered.

    """
    import math

    def power_of_two(n):
        f = math.log(n, 2)
        return f == math.floor(f)

    if power_of_two(height) and power_of_two(width):
        return gl.GL_TEXTURE_2D
    elif gli.have_extension('GL_ARB_texture_rectangle'):
        return gl.GL_TEXTURE_RECTANGLE_ARB
    else:
        raise HardwareError("Hardware does not support non-power-of-two"
                            " textures.")
