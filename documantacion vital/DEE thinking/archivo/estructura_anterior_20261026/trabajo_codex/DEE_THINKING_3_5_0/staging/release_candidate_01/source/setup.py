from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pybind11
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


ROOT = Path(__file__).resolve().parent


def _visual_studio_tools() -> tuple[str | None, str | None]:
    """Discover VS CMake/Ninja without pinning a machine-specific install."""

    vswhere = shutil.which("vswhere")
    if not vswhere:
        program_files_x86 = os.environ.get("ProgramFiles(x86)")
        if program_files_x86:
            candidate = Path(program_files_x86) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
            if candidate.is_file():
                vswhere = str(candidate)
    if not vswhere:
        return None, None
    query = [
        vswhere,
        "-latest",
        "-products", "*",
        "-requires", "Microsoft.VisualStudio.Component.VC.CMake.Project",
        "-property", "installationPath",
    ]
    result = subprocess.run(query, text=True, capture_output=True, check=False)
    installation = result.stdout.strip()
    if result.returncode != 0 or not installation:
        return None, None
    base = Path(installation) / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake"
    cmake = base / "CMake" / "bin" / "cmake.exe"
    ninja = base / "Ninja" / "ninja.exe"
    return (str(cmake) if cmake.is_file() else None,
            str(ninja) if ninja.is_file() else None)


class CMakeExtension(Extension):
    """A marker extension; CMake owns the complete native build graph."""

    def __init__(self, name: str) -> None:
        super().__init__(name=name, sources=[])


class CMakeBuild(build_ext):
    """Build the Python module from the same CMake product target as C++."""

    def build_extension(self, ext: Extension) -> None:
        extdir = Path(self.get_ext_fullpath(ext.name)).resolve().parent
        native_build_root = os.environ.get("DEE_THINKING_CMAKE_BUILD_ROOT")
        if native_build_root:
            build_temp = Path(native_build_root).resolve()
        else:
            build_temp = Path(tempfile.gettempdir()) / "dt35-wheel-cp313"
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir.mkdir(parents=True, exist_ok=True)

        vs_cmake, vs_ninja = _visual_studio_tools()
        cmake = os.environ.get("CMAKE_EXECUTABLE") or shutil.which("cmake") or vs_cmake
        if not cmake:
            raise RuntimeError(
                "CMake is required; put it on PATH or set CMAKE_EXECUTABLE"
            )

        ninja = os.environ.get("CMAKE_MAKE_PROGRAM") or shutil.which("ninja") or vs_ninja

        config = "Debug" if self.debug else "Release"
        cmake_args = [
            "-S", str(ROOT),
            "-B", str(build_temp),
            "-DDEE_THINKING_BUILD_TESTS=OFF",
            "-DDEE_THINKING_BUILD_EXAMPLES=OFF",
            "-DDEE_THINKING_BUILD_BENCHMARKS=OFF",
            "-DDEE_THINKING_BUILD_PYTHON=ON",
            f"-DDEE_THINKING_PYTHON_OUTPUT_DIR={extdir}",
            f"-DDEE_THINKING_PYTHON_VERSION={self.distribution.get_version()}",
            f"-DPython_EXECUTABLE={sys.executable}",
            f"-Dpybind11_DIR={pybind11.get_cmake_dir()}",
            f"-DCMAKE_BUILD_TYPE={config}",
        ]
        if ninja:
            cmake_args.extend(["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja}"])
        cxx = os.environ.get("CXX")
        if cxx:
            cmake_args.append(f"-DCMAKE_CXX_COMPILER={cxx}")

        # CMake's Ninja generator may be launched by the PEP 517 backend in a
        # subprocess that does not rediscover the Windows SDK manifest tools,
        # even though VsDevCmd made them available to the parent process.
        # Pin the tools that are actually visible to this build instead of
        # relying on a machine-specific absolute path.
        if os.name == "nt":
            rc = os.environ.get("DEE_THINKING_RC_COMPILER") or shutil.which("rc")
            mt = os.environ.get("DEE_THINKING_MT") or shutil.which("mt")
            if rc:
                cmake_args.append(
                    f"-DCMAKE_RC_COMPILER={Path(rc).resolve().as_posix()}"
                )
            if mt:
                cmake_args.append(f"-DCMAKE_MT={Path(mt).resolve().as_posix()}")

        env = os.environ.copy()
        env["DEE_THINKING_WHEEL_BUILD"] = "1"
        subprocess.run([cmake, *cmake_args], cwd=ROOT, env=env, check=True)
        subprocess.run(
            [cmake, "--build", str(build_temp), "--config", config,
             "--target", "dee_thinking_python", "--parallel"],
            cwd=ROOT,
            env=env,
            check=True,
        )

        expected = Path(self.get_ext_fullpath(ext.name)).resolve()
        if not expected.is_file():
            produced = sorted(extdir.glob("_native*.pyd" if os.name == "nt" else "_native*.so"))
            if len(produced) != 1:
                raise RuntimeError(
                    f"CMake did not produce the expected extension {expected}; found {produced}"
                )
            if produced[0] != expected:
                shutil.copy2(produced[0], expected)


setup(
    ext_modules=[CMakeExtension("dee_thinking._native")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
)
