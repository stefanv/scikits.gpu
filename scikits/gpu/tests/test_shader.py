from scikits.gpu.shader import *
from scikits.gpu.config import GLSLError

import nose
from nose.tools import *

from numpy.testing import *

def test_shader_creation():
    s = VertexShader("void main(void) { gl_Position = vec4(1,1,1,1); }")

def test_program_creation():
    s = VertexShader("void main(void) { gl_Position = vec4(1,1,1,1); }")
    p = Program(s)
    p.use()
    p.disable()

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
    v = VertexShader("""
uniform float float_in;
uniform int int_in;
uniform vec4 vec_in;
uniform mat4 mat_in;

varying float x;

void main(void)
{
    // Just some dummy statements used to test the passing of parameters
    // to the vertex shader
    x = float(int_in) * 0.5;
    x = float(int_in) + vec_in.r;
    x += mat_in[0];

    gl_Position = vec4(float_in, float(x), 0, 1);
}
""")

    p = Program(v)
    p.use()
    p['float_in'] = 1.3
    p['int_in'] = 1
    p['vec_in'] = [1.0, 2.0, 3.0, 4.0]
    p['mat_in'] = range(16)
    p.disable()

def test_if_in_use_decorator():
    s = VertexShader("""
    uniform float f;

    void main(void) {
      gl_Position = vec4(1,1,1,1);
    }
    """)
    p = Program(s)
    assert_raises(GLSLError, p.__setitem__, 'f', 1.3)

def test_uniform_active():
    s = default_vertex_shader()
    p = Program(s)
    assert_raises(GLSLError, p.__getitem__, 'f')

def test_query_uniform_without_binding():
    v = VertexShader("""
    uniform float f= 1.5;

    void main(void) {
      gl_Position = vec4(f,1,1,1);
    }""")
    p = Program(v)
    assert_equal(p['f'], 1.5)

def test_default_vertex_shader():
    s = default_vertex_shader()
    p = Program(s)

def test_program_failure():
    assert_raises(GLSLError, Program, [default_vertex_shader(),
                                       default_vertex_shader()])

def test_set_uniform_invalid_shape():
    s = VertexShader("""
    uniform vec4 x;

    void main(void) {
        gl_Position = x;
    }""")

    p = Program(s)
    p.use()
    assert_raises(ValueError, p.__setitem__, 'x', 1)
    assert_raises(ValueError, p.__setitem__, 'x', 1.0)
    assert_raises(ValueError, p.__setitem__, 'x', [1.0, 2.0])
    p.disable()

def test_uniform_types():
        v = VertexShader("""
uniform float float_in;
uniform int int_in;

uniform vec2 vec2_in;
uniform vec3 vec3_in;
uniform vec4 vec4_in;

uniform mat2 mat2_in;
uniform mat3 mat3_in;
uniform mat4 mat4_in;

uniform float float_arr[5];
uniform int int_arr[4];

uniform vec2 vec2_arr[2];
uniform vec3 vec3_arr[2];
uniform vec4 vec4_arr[2];

uniform mat2 mat2_arr[2];
uniform mat3 mat3_arr[3];
uniform mat4 mat4_arr[2];

varying float x;

void main(void) {
    // Dummy statement to make sure all uniforms become active
    x = float_in + float(int_in) + vec2_in.r + vec3_in.r + vec4_in.r +
        mat2_in[0] + mat3_in[0] + mat4_in[0] + float_arr[0] +
        float(int_arr[0]) + vec2_arr[0].r + vec3_arr[0].r +
        vec4_arr[0].r + mat2_arr[0][0] + mat3_arr[0][0] +
        mat4_arr[0][0];

    gl_Position = vec4(x, 0, 0, 0);
}
""")

        f = FragmentShader("""
        void main() {
            gl_FragColor = vec4(0, 0, 0, 0);
        }
        """)

        p = Program([v, f])
        p.use()

        def roundtrip_val(var, val):
            p[var] = val
            assert_array_equal(p[var].flat, val)

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
            yield roundtrip_val, var, val


def test_inconsistent_definitions():
    v = VertexShader("""
        uniform float float_in;

        void main(void) { gl_Position = vec4(0, 0, 0, 0); }
        """)

    f = FragmentShader("""
        uniform int float_in;

        void main(void) { gl_FragColor = vec4(0, 0, 0, 0); }
        """)

    assert_raises(GLSLError, Program, [v, f])
