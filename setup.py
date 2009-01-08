#! /usr/bin/env python

description = """Graphical Processing Unit (GPU) algorithms for scientific
computing.

Exploit the programmability of modern graphics cards via OpenGL GLSL
to do scientific calculations.  Provides a bridge between NumPy arrays
and the GPU, exposing OpenGL built-in functionality as well as custom
algorithms.

"""

import os
import sys

DISTNAME            = 'scikits.gpu'
DESCRIPTION         = 'GPU algorithms'
LONG_DESCRIPTION    = description
MAINTAINER          = 'Stefan van der Walt',
MAINTAINER_EMAIL    = 'stefan@sun.ac.za',
URL                 = 'http://scikits.appspot.com/gpu'
LICENSE             = 'MIT'
DOWNLOAD_URL        = URL
VERSION             = '0.1'

import setuptools
from numpy.distutils.core import setup

def configuration(parent_package='', top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'): os.remove('MANIFEST')

    from numpy.distutils.misc_util import Configuration
    config = Configuration(package_name, parent_package, top_path,
                           version = VERSION,
                           maintainer  = MAINTAINER,
                           maintainer_email = MAINTAINER_EMAIL,
                           description = DESCRIPTION,
                           license = LICENSE,
                           url = URL,
                           download_url = DOWNLOAD_URL,
                           long_description = LONG_DESCRIPTION)

    return config

if __name__ == "__main__":
    setup(configuration = configuration,
        install_requires = ['numpy', 'pyglet'],
        namespace_packages = ['scikits'],
        packages = setuptools.find_packages(),
        include_package_data = True,
        zip_safe = True, # the package can run out of an .egg file
        classifiers =
            [ 'Development Status :: 1 - Planning',
              'Environment :: Console',
              'Intended Audience :: Developers',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: BSD License',
              'Topic :: Scientific/Engineering'])
