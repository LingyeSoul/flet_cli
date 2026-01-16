#!/usr/bin/env python3
"""
Flet-Cli Auto Update Script for GitHub Actions
Automatically updates flet-cli to the latest version and integrates packn.py.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

try:
    from packaging.version import parse as parse_version
except ImportError:
    # Fallback if packaging not available
    parse_version = None

from integration_base import FletCliIntegrationBase


class FletCliAutoUpdater(FletCliIntegrationBase):
    """Auto-update flet-cli for GitHub Actions."""

    def __init__(self):
        self.repo_dir = Path.cwd()
        self.packn_file = self.repo_dir / "src" / "flet_cli" / "commands" / "packn.py"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_ref = os.getenv("GITHUB_REF", "")
        self.github_repository = os.getenv("GITHUB_REPOSITORY", "")

    def get_latest_flet_version(self) -> str:
        """Get the latest flet-cli version from GitHub."""
        print("[*] Fetching latest flet version from GitHub...")

        try:
            # Get latest release from GitHub API
            url = "https://api.github.com/repos/flet-dev/flet/releases/latest"
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"

            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode())

            tag_name = data.get("tag_name", "")
            # Remove 'v' prefix if present
            version = tag_name.lstrip("v")

            print(f"    [OK] Latest version: {version}")
            return version

        except Exception as e:
            print(f"    [ERROR] Failed to fetch latest version: {e}")
            sys.exit(1)

    def get_current_version(self) -> Optional[str]:
        """Get current version from pyproject.toml."""
        pyproject = self.repo_dir / "pyproject.toml"
        if not pyproject.exists():
            return None

        content = pyproject.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return None

    def integrate_packn(self, official_dir: Path, version: str):
        """Integrate packn.py into official version."""
        print("[*] Integrating packn.py...")

        # Copy essential files
        items_to_copy = ["src", "LICENSE"]
        for item in items_to_copy:
            src = official_dir / item
            dst = self.repo_dir / item

            if not src.exists():
                print(f"    [WARN] Skipping {item} (not found)")
                continue

            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()

            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

            print(f"    [OK] Copied {item}")

        # Update pyproject.toml
        self.update_pyproject_toml(version)

        # Update cli.py
        self.update_cli_py()

        # Create/update MANIFEST.in
        self.create_manifest_in()

        print("    [OK] Integration complete")

    def git_commit(self, version: str, branch: Optional[str] = None):
        """Commit changes to git."""
        print("[*] Committing changes to git...")

        # Configure git
        if self.github_token:
            # Use GitHub token for authentication
            subprocess.run(
                ["git", "config", "user.name", "github-actions[bot]"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
                check=True,
                capture_output=True
            )

        # Create or checkout branch
        if branch:
            # Create new branch for PR
            try:
                subprocess.run(
                    ["git", "checkout", "-b", branch],
                    check=True,
                    capture_output=True
                )
                print(f"    [OK] Created branch: {branch}")
            except subprocess.CalledProcessError:
                # Branch might already exist
                subprocess.run(
                    ["git", "checkout", branch],
                    check=True,
                    capture_output=True
                )
                print(f"    [OK] Checked out branch: {branch}")

        # Stage changes
        result = subprocess.run(
            ["git", "add", "src", "pyproject.toml", "MANIFEST.in", "LICENSE", "README.md"],
            capture_output=True,
            text=True
        )

        # Check if there are changes to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )

        if not status_result.stdout.strip():
            print("    [INFO] No changes to commit")
            return None

        # Commit
        commit_message = f"Update flet-cli to v{version}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"    [OK] Committed: {commit_message}")
            return commit_message
        else:
            print(f"    [ERROR] Failed to commit: {result.stderr}")
            return None

    def git_push(self, branch: Optional[str] = None):
        """Push changes to remote."""
        print("[*] Pushing to remote...")

        if branch:
            # Push specific branch
            result = subprocess.run(
                ["git", "push", "origin", branch],
                capture_output=True,
                text=True
            )
        else:
            # Push current branch
            result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:
            print("    [OK] Pushed successfully")
        else:
            print(f"    [ERROR] Failed to push: {result.stderr}")
            sys.exit(1)

    def create_pull_request(self, version: str, branch: str):
        """Create a pull request using GitHub CLI or API."""
        print(f"[*] Creating pull request...")

        # Try using gh CLI first
        try:
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", f"Update flet-cli to v{version}",
                    "--body", f"Automated update to flet-cli v{version} with packn.py integration.",
                    "--base", "main",
                    "--head", branch
                ],
                capture_output=True,
                text=True,
                check=True
            )
            print("    [OK] Pull request created")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            # gh CLI not available, try API
            pass

        # Use GitHub API
        if not self.github_token:
            print("    [WARN] GITHUB_TOKEN not set, skipping PR creation")
            return

        try:
            api_url = f"https://api.github.com/repos/{self.github_repository}/pulls"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "title": f"Update flet-cli to v{version}",
                "body": f"Automated update to flet-cli v{version} with packn.py integration.",
                "head": branch,
                "base": "main"
            }

            request = urllib.request.Request(
                api_url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers
            )
            request.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status == 201:
                    print("    [OK] Pull request created")
                else:
                    print(f"    [WARN] Failed to create PR: {response.status}")

        except Exception as e:
            print(f"    [WARN] Failed to create PR: {e}")

    def run(self, create_pr: bool = False, auto_merge: bool = False):
        """Run auto-update process."""
        print("="*60)
        print("Flet-Cli Auto Update")
        print("="*60)

        # Get versions
        latest_version = self.get_latest_flet_version()
        current_version = self.get_current_version()

        # Check if update needed (with None-safe comparison)
        if current_version and self._is_version_up_to_date(current_version, latest_version):
            print(f"\n[INFO] Already on latest version: {latest_version}")
            print("    No update needed.")
            return 0

        print(f"\nCurrent version: {current_version or 'unknown'}")
        print(f"Latest version:  {latest_version}")
        print(f"Update required: Yes\n")

        # Download and integrate
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            official_dir = self.download_flet_cli(latest_version, temp_path)
            self.integrate_packn(official_dir, latest_version)

        # Commit changes
        if create_pr:
            branch = f"update/flet-cli-{latest_version}"
            commit_msg = self.git_commit(latest_version, branch)
            if commit_msg:
                self.git_push(branch)
                self.create_pull_request(latest_version, branch)
        else:
            commit_msg = self.git_commit(latest_version)
            if commit_msg:
                self.git_push()

        print("\n" + "="*60)
        print("[SUCCESS] Update completed!")
        print("="*60)
        return 0

    def _is_version_up_to_date(self, current: str, latest: str) -> bool:
        """
        检查当前版本是否是最新的。

        使用语义版本比较而不是字符串比较。

        Args:
            current: 当前版本字符串
            latest: 最新版本字符串

        Returns:
            True 如果 current >= latest, 否则 False
        """
        if parse_version is not None:
            try:
                return parse_version(current) >= parse_version(latest)
            except Exception:
                # 如果版本解析失败，回退到字符串比较
                pass

        return current >= latest


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-update flet-cli for GitHub Actions"
    )
    parser.add_argument(
        "--create-pr",
        action="store_true",
        help="Create a pull request instead of pushing to main"
    )
    parser.add_argument(
        "--auto-merge",
        action="store_true",
        help="Auto-merge the pull request (requires additional permissions)"
    )

    args = parser.parse_args()

    try:
        updater = FletCliAutoUpdater()
        return updater.run(create_pr=args.create_pr, auto_merge=args.auto_merge)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
