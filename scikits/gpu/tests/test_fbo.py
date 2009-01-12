from nose.tools import *

from scikits.gpu.fbo import *

class TestFramebuffer(object):
    def create(self, x, y, colours):
        fbo = Framebuffer(x, y, colours)

    def test_creation(self):
        fbo = Framebuffer(64, 64)
        for bands in range(4):
            yield self.create, 16, 16, bands+1
