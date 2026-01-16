#!/usr/bin/env python3
"""
Flet-Cli Integration Base Module
提供共享的集成逻辑，消除 auto_update.py 和 integrate_packn.py 之间的代码重复。
"""
import os
import re
import shutil
import tarfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class FletCliIntegrationBase(ABC):
    """Flet-cli 集成操作的基类。"""

    # 常量
    GITHUB_API_BASE = "https://api.github.com/repos/flet-dev/flet"
    GITHUB_REPO_BASE = "https://github.com/flet-dev/flet"
    DEFAULT_AUTHOR = "Appveyor Systems Inc."
    DEFAULT_AUTHOR_EMAIL = "hello@flet.dev"
    DEFAULT_MAINTAINER = "LingyeSoul"
    DEFAULT_MAINTAINER_EMAIL = "lingyesoul@users.noreply.github.com"

    def __init__(self, repo_dir: Path):
        """
        初始化集成基类。

        Args:
            repo_dir: 仓库根目录
        """
        self.repo_dir = repo_dir
        self.packn_file = repo_dir / "src" / "flet_cli" / "commands" / "packn.py"

    def download_flet_cli(self, version: str, dest_dir: Path) -> Path:
        """
        下载并安全提取 flet-cli 源码档案。

        Args:
            version: 要下载的版本标签（如 "0.80.2" 或 "v0.80.2"）
            dest_dir: 提取到的目录

        Returns:
            提取目录的路径

        Raises:
            RuntimeError: 下载或提取失败
            ValueError: 版本格式无效
        """
        # 标准化版本号（确保有 v 前缀）
        normalized_version = version if version.startswith('v') else f'v{version}'

        # 验证版本格式
        self._validate_version(version)

        print(f"[*] 下载 flet-cli {version}...")

        # 使用正确的 release 下载 URL
        # 格式: https://github.com/flet-dev/flet/releases/download/v0.80.2/flet_cli-0.80.2.tar.gz
        url = f"{self.GITHUB_REPO_BASE}/releases/download/{normalized_version}/flet_cli-{version}.tar.gz"
        tar_path = dest_dir / f"flet-{version}.tar.gz"

        try:
            print(f"    URL: {url}")
            import urllib.request
            urllib.request.urlretrieve(url, tar_path)
            print(f"    [OK] 已下载")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # 尝试备用 URL（archive URL）
                print(f"    [WARN] Release asset 未找到，尝试 archive URL...")
                archive_url = f"{self.GITHUB_REPO_BASE}/archive/refs/tags/{normalized_version}.tar.gz"
                print(f"    备用 URL: {archive_url}")
                try:
                    urllib.request.urlretrieve(archive_url, tar_path)
                    print(f"    [OK] 已从 archive 下载")
                except Exception as e2:
                    raise RuntimeError(
                        f"下载 flet-cli 失败。\n"
                        f"Release URL: {url} (404)\n"
                        f"Archive URL: {archive_url} ({e2})"
                    )
            else:
                raise RuntimeError(f"下载 flet-cli 失败: {e}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"下载 flet-cli 失败（网络错误）: {e}")

        print("[*] 提取档案...")
        try:
            import tarfile
            with tarfile.open(tar_path, "r:gz") as tar:
                # 安全提取 - 防止路径遍历攻击
                self._safe_extract(tar, dest_dir)
            print(f"    [OK] 已提取")
        except (tarfile.TarError, OSError) as e:
            raise RuntimeError(f"提取档案失败: {e}")

        extracted_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise RuntimeError("提取后未找到目录")

        return extracted_dirs[0]

    def _safe_extract(self, tar, path):
        """
        安全提取 tar 档案，防止路径遍历攻击。

        Args:
            tar: tarfile 对象
            path: 提取目标路径

        Raises:
            RuntimeError: 检测到路径遍历尝试
        """
        def is_within_directory(directory, target):
            """检查目标是否在目录内。"""
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
            prefix = os.path.commonprefix([abs_directory, abs_target])
            return prefix == abs_directory

        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise RuntimeError(f"检测到路径遍历尝试: {member.name}")
            tar.extract(member, path)

    def _validate_version(self, version: str) -> None:
        """
        验证版本字符串格式。

        Args:
            version: 版本字符串

        Raises:
            ValueError: 版本格式无效
        """
        # 语义版本模式: X.Y.Z (可选 -suffix)
        pattern = r'^\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?$|^\d+\.\d+\.\d+$'

        if not re.match(pattern, version):
            raise ValueError(f"无效的版本格式: {version}")

    def update_cli_py(self, cli_file: Path) -> None:
        """
        更新 cli.py 以注册 packn 命令。

        Args:
            cli_file: cli.py 文件路径
        """
        print(f"    [*] 更新 cli.py...")

        if not cli_file.exists():
            print(f"        [WARN] 未找到 cli.py")
            return

        content = cli_file.read_text(encoding="utf-8")
        modified = False

        # 添加 import（如果需要）
        if "import flet_cli.commands.packn" not in content:
            content = re.sub(
                r'(import flet_cli\.commands\.pack\n)',
                r'\1import flet_cli.commands.packn\n',
                content
            )
            modified = True

        # 添加注册（如果需要）
        packn_registration = 'flet_cli.commands.packn.Command.register_to(sp, "packn")'
        if packn_registration not in content:
            content = content.replace(
                'flet_cli.commands.pack.Command.register_to(sp, "pack")',
                'flet_cli.commands.pack.Command.register_to(sp, "pack")\n'
                '    flet_cli.commands.packn.Command.register_to(sp, "packn")'
            )
            modified = True

        if modified:
            cli_file.write_text(content, encoding="utf-8")
            print("        [OK] 已更新")
        else:
            print("        [OK] 已是最新")

    def update_pyproject_toml(self, pyproject_file: Path, version: str) -> None:
        """
        使用自定义元数据更新 pyproject.toml。

        Args:
            pyproject_file: pyproject.toml 文件路径
            version: 新版本字符串
        """
        print("    [*] 更新 pyproject.toml...")

        content = pyproject_file.read_text(encoding="utf-8")

        # 更新版本
        content = re.sub(
            r'version\s*=\s*["\'][^"\']+["\']',
            f'version = "{version}"',
            content
        )

        # 更新描述
        content = re.sub(
            r'description\s*=\s*["\']Flet CLI[^"\']*["\']',
            'description = "Flet CLI with Nuitka packaging support for Windows"',
            content
        )

        # 确保维护者字段存在
        if "maintainers" not in content:
            authors_line = f'authors = [{{ name = "{self.DEFAULT_AUTHOR}", email = "{self.DEFAULT_AUTHOR_EMAIL}" }}]'
            maintainers_line = f'maintainers = [{{ name = "{self.DEFAULT_MAINTAINER}", email = "{self.DEFAULT_MAINTAINER_EMAIL}" }}]'
            content = content.replace(authors_line, f'{authors_line}\n{maintainers_line}')

        # 确保可选依赖存在
        if '[project.optional-dependencies]' not in content:
            content = content.replace(
                ']\n\n[project.urls]',
                ']\n\n[project.optional-dependencies]\nnuitka = ["nuitka"]\n\n[project.urls]'
            )

        pyproject_file.write_text(content, encoding="utf-8")
        print("        [OK] 已更新")

    def create_manifest_in(self, manifest_file: Path) -> None:
        """
        创建 MANIFEST.in（如果不存在）。

        Args:
            manifest_file: MANIFEST.in 文件路径
        """
        if not manifest_file.exists():
            print("    [*] 创建 MANIFEST.in...")
            content = """include README.md
include LICENSE
include pyproject.toml
recursive-include src/flet_cli/__pyinstaller *.dat
global-exclude __pycache__
global-exclude *.py[cod]
global-exclude *.pyo
global-exclude *.pyd
prune __pycache__
"""
            manifest_file.write_text(content, encoding="utf-8")
            print("        [OK] 已创建")
