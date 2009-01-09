from scikits.gpu.ntypes import *
import pyglet.gl as gl
from ctypes import c_byte

from nose.tools import *

def test_memory_type():
    assert_equal(memory_type(gl.GL_BYTE), gl.GLbyte)
    assert_equal(memory_type(c_byte), c_byte)
