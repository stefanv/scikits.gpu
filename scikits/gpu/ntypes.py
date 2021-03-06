"""Numeric types exchange between numpy, pyglet and ctypes.

"""

from pyglet import gl

opengl_ctypes = {
    gl.GL_BYTE: gl.GLbyte,
    gl.GL_UNSIGNED_BYTE: gl.GLubyte,
    gl.GL_SHORT: gl.GLshort,
    gl.GL_UNSIGNED_SHORT: gl.GLushort,
    gl.GL_INT: gl.GLint,
    gl.GL_UNSIGNED_INT: gl.GLuint,
    gl.GL_FLOAT: gl.GLfloat,
    gl.GL_DOUBLE: gl.GLdouble,
    }

ctypes_opengl = {
    gl.GLbyte: gl.GL_BYTE,
    gl.GLubyte: gl.GL_UNSIGNED_BYTE,
    gl.GLshort: gl.GL_SHORT,
    gl.GLushort: gl.GL_UNSIGNED_SHORT,
    gl.GLint: gl.GL_INT,
    gl.GLuint: gl.GL_UNSIGNED_INT,
    gl.GLfloat: gl.GL_FLOAT,
    gl.GLdouble: gl.GL_DOUBLE,
    }

def memory_type(T):
    """For a given OpenGL type, such as GL_BYTE, return the corresponding
    ctypes data-type, in this case c_ubyte.  If type is a ctype, it is simply
    passed through.

    Parameters
    ----------
    T : OpenGL type or ctype.

    Returns
    -------
    type : ctype
        The ctype corresponding to `T`.


    """
    if isinstance(T, type):
        return T
    elif isinstance(T, int):
        return opengl_ctypes[T]
    else:
        raise ValueError("Cannot convert provided type to ctype.")

