import setuptools
import os

# 避免在构建时直接导入flet_cli模块
def get_version():
    try:
        # 尝试直接导入
        from flet_cli.version import version
        return version
    except ImportError:
        # 如果导入失败，尝试从文件中读取版本
        try:
            version_file_path = os.path.join(os.path.dirname(__file__), "flet_cli", "version.py")
            with open(version_file_path, "r") as f:
                for line in f:
                    if line.startswith("version"):
                        return line.split("=")[1].strip().strip('"')
        except FileNotFoundError:
            # 如果还找不到文件，使用默认版本
            return "0.28.3"

version = get_version()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flet-cli",
    version=version,
    author="Appveyor Systems Inc.",
    author_email="hello@flet.dev",
    description="Flet CLI - a command-line utility for building, running, packaging Flet apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flet-dev/flet",
    project_urls={
        "Bug Tracker": "https://github.com/flet-dev/flet/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
    ],
    packages=["flet_cli", "flet_cli.commands", "flet_cli.utils"],
    python_requires=">=3.8",
    install_requires=[
        "flet>=0.28.0",
        "toml>=0.10.2",
        "click>=8.1.7",
    ],
    entry_points={
        "console_scripts": [
            "flet=flet_cli.cli:main",
        ],
    },
    include_package_data=True,
)