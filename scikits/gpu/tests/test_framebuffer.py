from nose.tools import *

from scikits.gpu.framebuffer import *
from pyglet.gl import *

class TestFramebuffer(object):
    def create(self, shape, dtype):
        fbo = Framebuffer()
        fbo.add_texture(shape, dtype=dtype)
        fbo.bind()
        fbo.unbind()
        del fbo

    def test_creation(self):
        fbo = Framebuffer()
        fbo.add_texture([64, 64])

        for dtype in [gl.GL_UNSIGNED_BYTE, gl.GL_BYTE,
                      gl.GL_INT, gl.GL_UNSIGNED_INT,
                      gl.GL_FLOAT]:
            for bands in [1, 2, 3, 4]:
                yield self.create, [16, 16, bands], dtype

    def test_bind_deleted(self):
        fbo = Framebuffer()
        fbo.add_texture([32, 32])
        fbo.__del__()
        assert_raises(RuntimeError, fbo.bind)

    def test_non_power_of_two_texture(self):
        fbo = Framebuffer()
        fbo.add_texture([32, 31])
