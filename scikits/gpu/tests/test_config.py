from nose.tools import *

from scikits.gpu.config import *
import pyglet.gl as gl

def test_requires_ext():
    assert_raises(HardwareSupportError, require_extension, 'blah')
    require_extension('GL_ARB_multitexture')

def test_hardware_info():
    info = hardware_info()
    assert(isinstance(info, dict))

def test_texture_target():
    assert_equal(texture_target(16, 16), gl.GL_TEXTURE_2D)
    assert texture_target(17, 16) in \
           [gl.GL_TEXTURE_2D, gl.GL_TEXTURE_RECTANGLE_ARB]
