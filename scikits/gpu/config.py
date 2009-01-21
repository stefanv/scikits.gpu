__all__ = ['HardwareSupportError', 'GLSLError', 'MAX_COLOR_ATTACHMENTS',
           'require_extension', 'hardware_info']

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

class DriverError(Exception):
    pass

class GLSLError(Exception):
    pass

def require_extension(ext):
    """Ensure that the given graphics extension is supported.

    """
    if not gl.gl_info.have_extension('GL_' + ext):
        raise HardwareSupportError("the %s extension" % ext)

hardware_info = {'vendor': gli.get_vendor(),
                 'renderer': gli.get_renderer(),
                 'version': gli.get_version()}

# Check hardware support

_opengl_version = hardware_info['version'].split(' ')[0]
if _opengl_version < "2.0":
    raise DriverError("This package requires OpenGL v2.0 or higher. "
                      "Your version is %s." % _opengl_version)

# This extension is required to return floats outside [0, 1]
# in gl_FragColor
require_extension('ARB_color_buffer_float')
require_extension('ARB_texture_float')

gl.glClampColorARB(gl.GL_CLAMP_VERTEX_COLOR_ARB, False)
gl.glClampColorARB(gl.GL_CLAMP_FRAGMENT_COLOR_ARB, False)
gl.glClampColorARB(gl.GL_CLAMP_READ_COLOR_ARB, False)
