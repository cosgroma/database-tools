#!/usr/bin/env python
import os
import re
import subprocess
import time
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


def read_requirements(path):
    with Path.open(path) as file:
        return file.read().splitlines()


version_file = Path("./src/databasetools/version.py")


def readme():
    with Path.open("README.md", encoding="utf-8") as f:
        content = f.read()
    return content


def get_git_hash():

    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ["SYSTEMROOT", "PATH", "HOME"]:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env["LANGUAGE"] = "C"
        env["LANG"] = "C"
        env["LC_ALL"] = "C"
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(["git", "rev-parse", "HEAD"])
        sha = out.strip().decode("ascii")
    except OSError:
        sha = "unknown"

    return sha


def get_hash():
    if Path.exists(Path(".git")):
        sha = get_git_hash()[:7]
    elif Path.exists(Path(version_file)):
        try:
            from .src.databasetools.version import __version__

            sha = __version__.split("+")[-1]
        except ImportError:
            sha = "unknown"
            # raise ImportError("Unable to get git version")
    else:
        sha = "unknown"

    return sha


def write_version_py():
    content = """# GENERATED VERSION FILE
# TIME: {}
__version__ = '{}'
__gitsha__ = '{}'
version_info = ({})
"""
    sha = get_hash()
    with Path.open("./VERSION") as f:
        SHORT_VERSION = f.read().strip()
    VERSION_INFO = ", ".join([x if x.isdigit() else f'"{x}"' for x in SHORT_VERSION.split(".")])

    version_file_str = content.format(time.asctime(), SHORT_VERSION, sha, VERSION_INFO)
    with Path.open(version_file, "w") as f:
        f.write(version_file_str)


# def get_version():
#     with Path.open(version_file) as f:
#         exec(compile(f.read(), version_file, "exec"))
#     return locals()["__version__"]


# def make_cuda_ext(name, module, sources, sources_cuda=None):
#     if sources_cuda is None:
#         sources_cuda = []
#     define_macros = []
#     extra_compile_args = {'cxx': []}

#     if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
#         define_macros += [('WITH_CUDA', None)]
#         extension = CUDAExtension
#         extra_compile_args['nvcc'] = [
#             '-D__CUDA_NO_HALF_OPERATORS__',
#             '-D__CUDA_NO_HALF_CONVERSIONS__',
#             '-D__CUDA_NO_HALF2_OPERATORS__',
#         ]
#         sources += sources_cuda
#     else:
#         print(f'Compiling {name} without CUDA')
#         extension = CppExtension

#     return extension(
#         name=f'{module}.{name}',
#         sources=[Path.join(*module.split('.'), p) for p in sources],
#         define_macros=define_macros,
#         extra_compile_args=extra_compile_args)


def get_requirements(filename="requirements.txt"):
    with Path.open(filename) as f:
        requires = [line.replace("\n", "") for line in f.readlines()]
    return requires


if __name__ == "__main__":
    # if '--cuda_ext' in sys.argv:
    #     ext_modules = [
    #         make_cuda_ext(
    #             name='deform_conv_ext',
    #             module='ops.dcn',
    #             sources=['src/deform_conv_ext.cpp'],
    #             sources_cuda=['src/deform_conv_cuda.cpp', 'src/deform_conv_cuda_kernel.cu']),
    #         make_cuda_ext(
    #             name='fused_act_ext',
    #             module='ops.fused_act',
    #             sources=['src/fused_bias_act.cpp'],
    #             sources_cuda=['src/fused_bias_act_kernel.cu']),
    #         make_cuda_ext(
    #             name='upfirdn2d_ext',
    #             module='ops.upfirdn2d',
    #             sources=['src/upfirdn2d.cpp'],
    #             sources_cuda=['src/upfirdn2d_kernel.cu']),
    #     ]
    #     sys.argv.remove('--cuda_ext')
    # else:
    #     ext_modules = []

    write_version_py()
    # setup(
    #     long_description=readme(),
    #     long_description_content_type='text/markdown',
    #     author='Xintao Wang',
    #     author_email='xintao.wang@outlook.com',
    #     keywords='computer vision, restoration, super resolution',
    #     url='https://github.com/xinntao/BasicSR',
    #     include_package_data=True,
    #     packages=find_packages(exclude=('options', 'datasets', 'experiments', 'results', 'tb_logger', 'wandb')),
    #     license='Apache License 2.0',
    #     setup_requires=['cython', 'numpy'],
    #     install_requires=get_requirements(),
    #     ext_modules=ext_modules,
    #     cmdclass={'build_ext': BuildExtension},
    #     zip_safe=False)

    setup(
        name="databasetools",
        # version=get_version(),
        version="0.0.0",
        license="LGPL-3.0-or-later",
        description="Document Database tools and helpers.",
        long_description="{}\n{}".format(
            re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
            re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
        ),
        author="Mathew Cosgrove",
        author_email="cosgroma@gmail.com",
        url="https://github.com/cosgroma/database-tools",
        packages=find_packages("src"),
        package_dir={"": "src"},
        py_modules=[path.stem for path in Path("src").glob("*.py")],
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)" "Operating System :: Unix",
            "Operating System :: POSIX",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Utilities",
        ],
        project_urls={
            "Changelog": "https://github.com/cosgroma/database-tools/blob/master/CHANGELOG.rst",
            "Issue Tracker": "https://github.com/cosgroma/database-tools/issues",
        },
        keywords=[
            # eg: "keyword1", "keyword2", "keyword3",
        ],
        python_requires=">=3.11",
        install_requires=get_requirements(),
        extras_require={
            #   "rst": ["docutils>=0.11"],
            #   ":python_version=='3.8'": ["backports.zoneinfo"],
        },
        entry_points={
            "console_scripts": [
                "dbman = databasetools.cli:run",
            ]
        },
    )
