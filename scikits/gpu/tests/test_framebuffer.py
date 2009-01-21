from nose.tools import *

from scikits.gpu.config import MAX_COLOR_ATTACHMENTS
from scikits.gpu.framebuffer import *
from pyglet.gl import *

import warnings

class TestFramebuffer(object):
    def create(self, shape, dtype):
        fbo = Framebuffer()

        warnings.filterwarnings('ignore')
        fbo.add_texture(shape, dtype=dtype)
        warnings.filterwarnings('once')

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

    def test_max_attachments(self):
        fbo = Framebuffer()
        for i in range(MAX_COLOR_ATTACHMENTS):
            fbo.add_texture([16, 16])

        assert_raises(RuntimeError, fbo.add_texture, [16, 16])
