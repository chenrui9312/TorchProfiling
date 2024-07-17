import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read("python/module_logging/config.ini")

script_dir = os.path.dirname(os.path.abspath(__file__))


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)
        # Install .pth file
        src = os.path.join(os.path.dirname(__file__), "module_logging.pth")
        install_lib = self.get_finalized_command("install_lib").install_dir
        dst = os.path.join(install_lib, os.path.basename(src))
        self.copy_file(src, dst)

    def build_extension(self, ext):
        ninja_args = []
        enable_cuda = os.environ.get("CUDA_DEV")

        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY="
            + os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name))),
            "-DPYTHON_EXECUTABLE=" + sys.executable,
            "-DCMAKE_INSTALL_PREFIX="
            + os.path.join(
                os.path.abspath(os.path.dirname(self.build_lib)),
                os.path.basename(self.build_lib),
            ),
            "-DPYBIND11_GET_OPINFO=" + pybind11.__path__[0],
            "-DCMAKE_GENERATOR=Ninja",
            # '-DCUDA_DEV',
            # '-DPYTHON_INCLUDE_DIR=' + os.environ.get('PYTHON_INCLUDE_DIR'),
            # '-DPYTHON_LIBRARY=' + os.environ.get('PYTHON_LIBRARY'),
            # f'-B {os.path.join(script_dir, "build")}',
        ]
        if enable_cuda == "true":
            cmake_args.append("-DCUDA_DEV=TRUE")

        # if publish_build:
        # cmake_args.append('-DPYTHON_INCLUDE_DIR=' + os.environ.get('PYTHON_INCLUDE_DIR'))
        # cmake_args.append('-DPYTHON_LIBRARY=' + os.environ.get('PYTHON_LIBRARY'))
        # cmake_args.append('-DPUBLISH_BUILD=ON')

        build_dir = os.path.abspath(os.path.join(self.build_temp, ext.name))
        os.makedirs(build_dir, exist_ok=True)

        subprocess.check_call(
            ["cmake", f"{script_dir}"] + cmake_args + ninja_args, cwd=build_dir
        )
        print(f"cmake build_dir {build_dir}")
        subprocess.check_call(["cmake", "--build", "."], cwd=build_dir)


def regular_setup():
    setup(
        name="module_logging",
        version="1.0.0",
        author="Eric.Wang",
        author_email="https://github.com/wffpy/TorchProfiling",
        description="logging on moudle and aten op level",
        packages=find_packages(where="python"),
        package_dir={"": os.path.join(script_dir, "python")},
        package_data={"": ["*"]},
        #install_requires=[
        #    "torch",
        #],
        entry_points={
            "console_scripts": ["module_logging = module_logging.__main__:main"]
        },
        zip_safe=False,
    )


def cpp_extend_setup():
    setup(
        name="module_logging",
        version="1.0.0",
        author="Eric.Wang",
        author_email="https://github.com/wffpy/TorchProfiling",
        description="logging on moudle and aten op level",
        packages=find_packages(where="python"),
        package_dir={"": os.path.join(script_dir, "python")},
        package_data={"": ["*"]},
        install_requires=[
            "prettytable",
        ],
        entry_points={
            "console_scripts": ["module_logging = module_logging.__main__:main"]
        },
        ext_modules=[
            CMakeExtension("module_logging.Hook"),
        ],
        cmdclass=dict(build_ext=CMakeBuild),
        zip_safe=False,
    )


if __name__ == "__main__":
    compile_option = os.environ.get("COMPIEL_OPTION")
    if compile_option is not None:
        config["database"]["cpp_extend"] = "False"
        with open("python/module_logging/config.ini", "w") as configfile:
            config.write(configfile)
        regular_setup()
    else:
        config["database"]["cpp_extend"] = "True"
        with open("python/module_logging/config.ini", "w") as configfile:
            config.write(configfile)
        cpp_extend_setup()
