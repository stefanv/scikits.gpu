from nose.tools import *

from scikits.gpu.texture import *
import pyglet.gl as gl

def test_creation():
    Texture(20, 20)
    Texture(20, 25)

#def test_texture_target():
#    assert_equal(texture_target(16, 16), gl.GL_TEXTURE_2D)
#    assert texture_target(17, 16) in \
#           [gl.GL_TEXTURE_2D, gl.GL_TEXTURE_RECTANGLE_ARB]
