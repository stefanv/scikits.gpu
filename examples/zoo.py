from scikits.gpu.api import *

def mandelbrot():
    """Return shaders for generating Mandelbrot fractals.

    GLSL code based on http://nuclear.sdf-eu.org/articles/sdr_fract
    by John Tsiombikas

    Uniforms
    --------
    offset : vec2
        Position at which the fractal is calculated.
    width_ratio : float
        The aspect ratio of the screen: width/height.
    zoom : float
        Zoom factor.

    """
    v = VertexShader("""
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

    f = FragmentShader("""
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

    return v, f
