from scikits.gpu.api import *
import pyglet.window
from pyglet import gl
from zoo import mandelbrot

window = pyglet.window.Window(width=800, height=600)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
gl.glLoadIdentity()

p = Program(mandelbrot())
p.bind()
p['offset'] = [-1.0, 0.0]
p['width_ratio'] = 800/600.
p['zoom'] = 2.0

# Draw full-screen canvas
gl.glBegin(gl.GL_QUADS)
for coords in [(-1.0, -1.0),
               ( 1.0, -1.0),
               ( 1.0,  1.0),
               (-1.0,  1.0)]:
    gl.glVertex3f(coords[0], coords[1], 0.0)

gl.glEnd()
gl.glFlush()

p.unbind()

pyglet.app.run()
