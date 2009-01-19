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

    p['float_in'] = 1.3
    p['int_in'] = 1
    p['vec_in'] = [1.0, 2.0, 3.0, 4.0]
    p['mat_in'] = range(16)
    p.unbind()

def test_if_bound_decorator():
    s = Shader("void main(void) { gl_Position = vec4(1,1,1,1);}")
    p = Program(s)
    assert_raises(GLSLError, p.__setitem__, 'float_in', 1.3)

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
    assert_raises(ValueError, p.__setitem__, 'x', 1)
    assert_raises(ValueError, p.__setitem__, 'x', 1.0)
    p.unbind()

def test_uniform_types():
        s = VertexShader("""
uniform float float_in;
uniform int int_in;

uniform vec2 vec2_in;
uniform vec3 vec3_in;
uniform vec4 vec4_in;

uniform mat2 mat2_in;
uniform mat3 mat3_in;
uniform mat4 mat4_in;

uniform float float_arr[];
uniform int int_arr[3];

uniform vec2 vec2_arr[];
uniform vec3 vec3_arr[];
uniform vec4 vec4_arr[12];

uniform mat2 mat2_arr[];
uniform mat3 mat3_arr[12];
uniform mat4 mat4_arr[];

varying float x;

void main(void) { gl_Position = vec4(0, 0, 0, 0); }
""")

        p = Program(s)
        p.bind()

        def upload_val(var, val):
            p[var] = val

        for var, val in [('float_in', 1.0),
                         ('int_in', 3),
                         ('vec2_in', [1, 2]),
                         ('vec3_in', [1, 2, 3]),
                         ('vec4_in', [1, 2, 3, 4]),
                         ('mat2_in', [float(x) for x in range(4)]),
                         ('mat3_in', [float(x) for x in range(9)]),
                         ('mat4_in', [float(x) for x in range(16)]),
                         ('float_arr', [float(x) for x in range(5)]),
                         ('int_arr', range(4)),
                         ('vec2_arr', range(4)),
                         ('vec3_arr', range(6)),
                         ('vec4_arr', range(8)),
                         ('mat2_arr', [float(x) for x in range(8)]),
                         ('mat3_arr', [float(x) for x in range(27)]),
                         ('mat4_arr', [float(x) for x in range(32)])]:
            yield upload_val, var, val

        assert_raises(ValueError, upload_val, x, 3.0)

def test_inconsistent_definitions():
    v = VertexShader("""
        uniform float float_in;

        void main(void) { gl_Position = vec4(0, 0, 0, 0); }
        """)

    f = FragmentShader("""
        uniform int float_in;

        void main(void) { gl_FragColor = vec4(0, 0, 0, 0); }
        """)

    p = Program([v, f])

    assert_raises(GLSLError, p.bind)
