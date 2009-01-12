from nose.tools import *

from scikits.gpu.fbo import *

class TestFramebuffer(object):
    def create(self, x, y, colours):
        fbo = Framebuffer(x, y, colours)
        fbo.bind()
        fbo.unbind()
        fbo.delete()

    def test_creation(self):
        fbo = Framebuffer(64, 64)
        for bands in [1, 2, 3, 4]:
            yield self.create, 16, 16, bands
