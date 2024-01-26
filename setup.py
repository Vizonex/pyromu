from setuptools import Extension, setup , find_packages
from Cython.Build import cythonize



__version__ = "0.0.1"
__author__ = "Vizonex"


def do_installation():
    ext = Extension("pyromu._pyromu", ["pyromu/_pyromu.pyx"],
        # we need to optimize otherwise we could end up being slower than intended...
        extra_compile_args=["/O2"]
    )

    setup(
        name="pyromu",
        author=__author__,
        version=__version__,
        ext_modules=cythonize(ext),
        packages=find_packages(include="pyromu*"),
        classifiers=[
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Intended Audience :: Developers'
        ],
        include_package_data=True,
        install_requires=["cython"],
        description="A Faster Version of the python random stdlib libary written in cython",
        license="MIT",
    )

if __name__ == "__main__":
    do_installation()
