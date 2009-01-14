from scikits.gpu.shader import *
from scikits.gpu.config import GLSLError

from nose.tools import *

def test_shader_creation():
    s = Shader("void main(void) { gl_Position = vec4(1,1,1,1); }")

def test_program_creation():
    s = Shader("void main(void) { gl_Position = vec4(1,1,1,1); }")
    p = Program(s)
    p.bind()
    p.unbind()

def test_vertex_shader():
    s = VertexShader("void main(void) { gl_Position = vec4(1,1,1,1); }");

def test_fragment_shader():
    s = FragmentShader("void main(void) { gl_FragColor = vec4(1,1,1,1); }");

def test_program():
    v = VertexShader("""
varying float x, y;

void main(void)
{
  x = (clamp(gl_Vertex.x, 0.0, 1.0));
  y = (clamp(gl_Vertex.y, 0.0, 1.0));

  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
""")

    f = FragmentShader("""
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

    p = Program([v, f])

def test_parameters():
    s = VertexShader("""
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

    p = Program(s)
    p.bind()

    p.uniformf('float_in', 1.3)
    p.uniformi('int_in', 1)
    p.uniformf('vec_in', [1.0, 2.0, 3.0, 4.0])
    p.uniform_matrixf('mat_in', range(16))
    p.unbind()

def test_if_bound_decorator():
    s = Shader("void main(void) { gl_Position = vec4(1,1,1,1);}")
    p = Program(s)
    assert_raises(GLSLError, p.uniformf, 'float_in', 1.3)

def test_default_vertex_shader():
    s = default_vertex_shader()
    p = Program(s)

def test_program_failure():
    assert_raises(GLSLError, Program, [default_vertex_shader(),
                                       default_vertex_shader()])

def test_set_uniform_invalid_type():
    s = default_vertex_shader()
    p = Program(s)
    p.bind()
    assert_raises(ValueError, p.uniformf, 'x', 1)
    assert_raises(ValueError, p.uniformi, 'x', 1.0)
    p.unbind()
