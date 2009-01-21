from nose.tools import *

from scikits.gpu.config import *
import pyglet.gl as gl

def test_requires_ext():
    assert_raises(HardwareSupportError, require_extension, 'blah')
    require_extension('ARB_multitexture')

def test_hardware_info():
    assert(isinstance(hardware_info, dict))
