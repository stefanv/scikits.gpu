"""Render Mandelbrot fractal offscreen.  Note that this is beta code, and the
APIs are bound to change over the next couple of days.

"""

from scikits.gpu.api import *
import pyglet.window
from pyglet import gl
import zoo

WIDTH, HEIGHT = 800, 600

def draw_canvas():
    # Draw full-screen canvas
    gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0_EXT)
    gl.glBegin(gl.GL_QUADS)
    for coords in [(-1.0, -1.0),
                   (1.0, -1.0),
                   (1.0, 1.0),
                   (-1.0,  1.0)]:
        gl.glVertex3f(coords[0], coords[1], 0.0)

    gl.glEnd()


# Create framebuffer object and attach texture to it
fbo = Framebuffer()
fbo.add_texture([WIDTH, HEIGHT, 3], dtype=gl.GL_FLOAT)
gl.glPushAttrib(gl.GL_VIEWPORT_BIT)
gl.glViewport(0, 0, WIDTH, HEIGHT)

# Set the framebuffer as the current rendering output
fbo.bind()

gl.glClear(gl.GL_COLOR_BUFFER_BIT)
gl.glLoadIdentity()

# Intialise the shader program
p = Program(zoo.mandelbrot())
p.bind()

# Setup the Mandelbrot fractal parameters
p['offset'] = [-1.0, 0.0]
p['width_ratio'] = float(WIDTH)/HEIGHT
p['zoom'] = 2.0

# Draw on the framebuffer
draw_canvas()

p.unbind()


# Copy the data from the graphics card to system memory

import numpy as np
import ctypes

arr = np.empty((HEIGHT, WIDTH, 3), dtype=np.float32)

gl.glFinish()
gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0_EXT)
gl.glReadPixels(0, 0, WIDTH, HEIGHT, gl.GL_RGB, gl.GL_FLOAT,
                arr.ctypes.data)

# Display using matplotlib (TODO: use opengl to display)

import matplotlib.pyplot as plt
plt.imshow(arr)
plt.show()

fbo.unbind()
gl.glPopAttrib()
