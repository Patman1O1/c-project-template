#!/usr/bin/env python3

from pathlib import Path
import argparse
import shutil
import subprocess

# Parse commandline arguments
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("conan_profile", help="Conan profile name", type=str)
parser.add_argument("build_type", help="CMake build type", type=str)
args: argparse.Namespace = parser.parse_args()

# Set project directories
source_dir: Path = Path(__file__).parent
binary_dir: Path = source_dir/"build"

# Set Conan toolchain file path
conan_toolchain: Path = binary_dir/f"{args.build_type}/generators/conan_toolchain.cmake"

# Create the Conan process
conan_process: subprocess.Popen[str] = subprocess.Popen(
    ["conan", "install", f"{source_dir}", f"--profile={args.conan_profile}", "-s", f"build_type={args.build_type}", "--build=missing"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Print the output
for line in conan_process.stdout:
    print(line, end="")

conan_process.wait()
if conan_process.returncode != 0:
    raise RuntimeError("Conan install failed")

# Create the CMake configure process
cmake_configure_process: subprocess.Popen[str] = subprocess.Popen(
    ["cmake", "-S", f"{source_dir}", "-B", f"{binary_dir}", "-D", f"CMAKE_TOOLCHAIN_FILE={conan_toolchain}", "-D", f"CMAKE_BUILD_TYPE={args.build_type}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Print the output
for line in cmake_configure_process.stdout:
    print(line, end="")

cmake_configure_process.wait()
if cmake_configure_process.returncode != 0:
    raise RuntimeError("CMake configuration step failed")


