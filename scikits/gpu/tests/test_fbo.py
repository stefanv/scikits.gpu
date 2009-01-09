from nose.tools import *

from scikits.gpu.fbo import *

class TestFramebuffer(object):
    def test_creation(self):
        fbo = Framebuffer(16, 16)
        for bands in range(4):
            fbo = Framebuffer(16, 16, bands+1)
