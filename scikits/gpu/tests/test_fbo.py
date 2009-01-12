from nose.tools import *

from scikits.gpu.fbo import *
from pyglet.gl import *

class TestFramebuffer(object):
    def create(self, x, y, colours, dtype):
        fbo = Framebuffer(x, y, bands=colours, dtype=dtype)
        fbo.bind()
        fbo.unbind()
        fbo.delete()

    def test_creation(self):
        fbo = Framebuffer(64, 64)
        for dtype in [gl.GL_UNSIGNED_BYTE, gl.GL_BYTE,
                      gl.GL_INT, gl.GL_UNSIGNED_INT,
                      gl.GL_FLOAT]:
            for bands in [1, 2, 3, 4]:
                yield self.create, 16, 16, bands, dtype

    def test_bind_deleted(self):
        fbo = Framebuffer(32, 32)
        fbo.delete()
        assert_raises(RuntimeError, fbo.bind)
