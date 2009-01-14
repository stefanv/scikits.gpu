from scikits.gpu.api import *
import pyglet.window
from pyglet import gl

# GLSL code based on http://nuclear.sdf-eu.org/articles/sdr_fract
# by John Tsiombikas

v_shader = VertexShader("""
uniform vec2 offset;
uniform float zoom;
uniform float width_ratio;

varying vec2 pos;

void main(void) {
    pos.x = gl_Vertex.x * width_ratio / zoom + offset.x;
    pos.y = gl_Vertex.y / zoom + offset.y;
    gl_Position = ftransform();
}
""")

f_shader = FragmentShader("""
varying vec2 pos;

void main() {
    float k;
    float r = 0.0, i = 0.0;
    float a, b;
    for (k = 0.0; k < 1.0; k += 0.005) {
        a = r*r - i*i + pos.x;
        b = 2*r*i + pos.y;

        if ((a*a + b*b) > 4) break;

        r = a;
        i = b;
    }

    gl_FragColor = vec4(k, 3*sin(k), sin(k*3.141/2.), 1.0);
}
""")

window = pyglet.window.Window(width=800, height=600)
gl.glClear(gl.GL_COLOR_BUFFER_BIT)
gl.glLoadIdentity()

p = Program([v_shader, f_shader])
p.bind()
p.uniformf('offset', [-1.0, 0.0])
p.uniformf('width_ratio', 800/600.)
p.uniformf('zoom', 2.0)

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
