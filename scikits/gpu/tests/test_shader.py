from scikits.gpu.shader import *
from scikits.gpu.config import GLSLError

from nose.tools import *

def test_creation():
    s = Shader()
    s.bind()
    s.unbind()

def test_program():
    s = Shader(vert="""
varying float x, y;

void main(void)
{
  x = (clamp(gl_Vertex.x, 0.0, 1.0));
  y = (clamp(gl_Vertex.y, 0.0, 1.0));

  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
""",
               frag="""
varying float xpos;

void main(void)
{
    float i = 0.0;
    while(i < 1.0)
    {
        i += 0.1;
    }
    gl_FragColor = vec4(i, i, sin(i*2.0), 1.0);
}

               """)

def test_parameters():
    s = Shader(vert="""
uniform float float_in;
uniform int int_in;
uniform vec4 vec_in;
uniform mat4 mat_in;

varying float x;

void main(void)
{
    // Just some dummy statements used to test the passing of parameters
    // to the vertex shader
    x = float_in;
    x = float(int_in) * 0.5;
    x = float(int_in) + vec_in.r;

    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
    """)

    s.bind()
    s.uniformf('float_in', 1.3)
    s.uniformi('int_in', 1)
    s.uniformf('vec_in', 1.0, 2.0, 3.0, 4.0)
    s.uniform_matrixf('mat_in', range(16))
    s.unbind()

def test_if_bound_decorator():
    s = Shader()
    assert_raises(GLSLError, s.uniformf, 'float_in', 1.3)
