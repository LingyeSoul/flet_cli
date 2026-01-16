#!/usr/bin/env python3
"""
Flet-Cli Integration Script
Automatically integrate custom packn.py into new flet-cli versions.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


class FletCliIntegrator:
    """Automatically integrate packn.py into flet-cli."""

    def __init__(
        self,
        version: str,
        source_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        self.version = version
        self.source_dir = source_dir or Path(__file__).parent
        self.output_dir = output_dir or self.source_dir
        self.packn_file = self.source_dir / "src" / "flet_cli" / "commands" / "packn.py"

        # Verify packn.py exists
        if not self.packn_file.exists():
            raise FileNotFoundError(f"packn.py not found at {self.packn_file}")

    def download_flet_cli(self, dest_dir: Path) -> Path:
        """Download and extract flet-cli source from GitHub."""
        print(f"[*] Downloading flet-cli version {self.version}...")

        # GitHub archive URL
        url = f"https://github.com/flet-dev/flet/archive/refs/tags/{self.version}.tar.gz"
        tar_path = dest_dir / f"flet-cli-{self.version}.tar.gz"

        try:
            print(f"    Downloading from: {url}")
            urllib.request.urlretrieve(url, tar_path)
            print(f"    [OK] Downloaded to {tar_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to download flet-cli: {e}")

        # Extract tar.gz
        print(f"[*] Extracting archive...")
        try:
            import tarfile

            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(dest_dir)
            print(f"    [OK] Extracted")
        except Exception as e:
            raise RuntimeError(f"Failed to extract archive: {e}")

        # Find extracted directory
        extracted_dirs = [d for d in dest_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise RuntimeError("No directory found after extraction")

        extracted_dir = extracted_dirs[0]
        print(f"    [OK] Extracted to {extracted_dir}")

        return extracted_dir

    def backup_current(self) -> Path:
        """Backup current directory."""
        backup_dir = self.output_dir / f".backup_{self.version}"
        print(f"[*] Creating backup at {backup_dir}...")

        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        # Copy only essential files
        essential_items = ["src", "pyproject.toml", "README.md", "LICENSE", "MANIFEST.in"]

        for item in essential_items:
            src = self.output_dir / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, backup_dir / item)
                else:
                    shutil.copy2(src, backup_dir)

        print(f"    [OK] Backup created")
        return backup_dir

    def integrate_packn(self, official_dir: Path):
        """Integrate packn.py into official version."""
        print(f"[*] Integrating packn.py...")

        # 1. Copy packn.py to official version
        official_commands_dir = official_dir / "src" / "flet_cli" / "commands"
        target_packn = official_commands_dir / "packn.py"

        shutil.copy2(self.packn_file, target_packn)
        print(f"    [OK] Copied packn.py")

        # 2. Update cli.py to register packn command
        cli_file = official_dir / "src" / "flet_cli" / "cli.py"
        self.update_cli_py(cli_file)

        # 3. Update pyproject.toml
        pyproject_file = official_dir / "pyproject.toml"
        self.update_pyproject_toml(pyproject_file)

        # 4. Create MANIFEST.in if not exists
        manifest_file = official_dir / "MANIFEST.in"
        self.create_manifest_in(manifest_file)

        print(f"    [OK] Integration complete")

    def update_cli_py(self, cli_file: Path):
        """Update cli.py to register packn command."""
        print(f"    [*] Updating cli.py...")

        content = cli_file.read_text(encoding="utf-8")

        # Add import if not exists
        if "import flet_cli.commands.packn" not in content:
            # Find the import section
            import_section = []
            for line in content.split("\n"):
                import_section.append(line)
                if line.startswith("import flet_cli.commands.pack"):
                    # Insert after pack import
                    import_section.append("import flet_cli.commands.packn")
                    break

            content = "\n".join(import_section)

        # Add registration if not exists
        if 'flet_cli.commands.packn.Command.register_to(sp, "packn")' not in content:
            # Find registration section and add packn after pack
            content = content.replace(
                'flet_cli.commands.pack.Command.register_to(sp, "pack")',
                'flet_cli.commands.pack.Command.register_to(sp, "pack")\n'
                '    flet_cli.commands.packn.Command.register_to(sp, "packn")'
            )

        cli_file.write_text(content, encoding="utf-8")
        print(f"        [OK] Registered packn command")

    def update_pyproject_toml(self, pyproject_file: Path):
        """Update pyproject.toml with custom metadata."""
        print(f"    [*] Updating pyproject.toml...")

        content = pyproject_file.read_text(encoding="utf-8")

        # Update description
        content = content.replace(
            'description = "Flet CLI"',
            'description = "Flet CLI with Nuitka packaging support for Windows"'
        )

        # Add maintainers if not exists
        if "maintainers" not in content:
            content = content.replace(
                'authors = [{ name = "Appveyor Systems Inc.", email = "hello@flet.dev" }]',
                'authors = [{ name = "Appveyor Systems Inc.", email = "hello@flet.dev" }]\n'
                'maintainers = [{ name = "LingyeSoul", email = "lingyesoul@users.noreply.github.com" }]'
            )

        # Add optional nuitka dependency if not exists
        if '[project.optional-dependencies]' not in content:
            content = content.replace(
                ']\n\n[project.urls]',
                ']\n\n[project.optional-dependencies]\nnuitka = ["nuitka"]\n\n[project.urls]'
            )

        pyproject_file.write_text(content, encoding="utf-8")
        print(f"        [OK] Updated project metadata")

    def create_manifest_in(self, manifest_file: Path):
        """Create MANIFEST.in if not exists."""
        if not manifest_file.exists():
            print(f"    [*] Creating MANIFEST.in...")
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
            print(f"        [OK] Created MANIFEST.in")

    def copy_to_output(self, source_dir: Path):
        """Copy integrated version to output directory."""
        print(f"[*] Copying to output directory {self.output_dir}...")

        # Backup packn.py if it exists in output
        packn_backup = None
        if self.packn_file.exists():
            print("    [INFO] Backing up packn.py...")
            packn_backup = self.packn_file.read_text(encoding="utf-8")

        # Files and directories to copy
        items_to_copy = [
            "src",
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "MANIFEST.in",
        ]

        for item in items_to_copy:
            src = source_dir / item
            dst = self.output_dir / item

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

        # Restore packn.py if it was deleted
        if not self.packn_file.exists() and packn_backup is not None:
            print("    [INFO] Restoring packn.py...")
            self.packn_file.parent.mkdir(parents=True, exist_ok=True)
            self.packn_file.write_text(packn_backup, encoding="utf-8")
            print("    [OK] packn.py restored")

        # Update configuration files
        print("[*] Updating configuration files...")

        # Update pyproject.toml
        pyproject_file = self.output_dir / "pyproject.toml"
        self.update_pyproject_toml(pyproject_file)

        # Update cli.py
        cli_file = self.output_dir / "src" / "flet_cli" / "cli.py"
        self.update_cli_py(cli_file)

        # Create MANIFEST.in if not exists
        manifest_file = self.output_dir / "MANIFEST.in"
        self.create_manifest_in(manifest_file)

        print("    [OK] Configuration updated")

    def verify_integration(self):
        """Verify the integration was successful."""
        print(f"[*] Verifying integration...")

        checks = [
            ("packn.py", self.output_dir / "src" / "flet_cli" / "commands" / "packn.py"),
            ("cli.py", self.output_dir / "src" / "flet_cli" / "cli.py"),
            ("pyproject.toml", self.output_dir / "pyproject.toml"),
            ("MANIFEST.in", self.output_dir / "MANIFEST.in"),
        ]

        all_ok = True
        for name, path in checks:
            if path.exists():
                print(f"    [OK] {name} exists")
            else:
                print(f"    [FAIL] {name} missing")
                all_ok = False

        # Check if packn is registered in cli.py
        cli_file = self.output_dir / "src" / "flet_cli" / "cli.py"
        if cli_file.exists():
            content = cli_file.read_text(encoding="utf-8")
            if "import flet_cli.commands.packn" in content:
                print(f"    [OK] packn import found in cli.py")
            else:
                print(f"    [FAIL] packn import missing in cli.py")
                all_ok = False

            if 'flet_cli.commands.packn.Command.register_to(sp, "packn")' in content:
                print(f"    [OK] packn registration found in cli.py")
            else:
                print(f"    [FAIL] packn registration missing in cli.py")
                all_ok = False

        return all_ok

    def run(self, backup: bool = True, verify: bool = True):
        """Run the integration process."""
        print("="*60)
        print(f"Flet-Cli Integration Script v{self.version}")
        print("="*60)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Download official version
            official_dir = self.download_flet_cli(temp_path)

            # Backup current version
            if backup:
                self.backup_current()

            # Integrate packn.py
            self.integrate_packn(official_dir)

            # Copy to output
            self.copy_to_output(official_dir)

            # Verify
            if verify:
                if self.verify_integration():
                    print("\n" + "="*60)
                    print("[SUCCESS] Integration completed successfully!")
                    print("="*60)
                else:
                    print("\n" + "="*60)
                    print("[WARNING] Integration completed but verification failed!")
                    print("="*60)
                    return 1

        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print("  2. Test the build: python -m build")
        print("  3. Install locally: pip install -e .")
        print("  4. Test packn command: flet-cli packn --help")

        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Integrate packn.py into flet-cli official release"
    )
    parser.add_argument(
        "version",
        help="Flet-cli version to integrate (e.g., 0.80.2)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip verification",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source directory containing packn.py (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: current directory)",
    )

    args = parser.parse_args()

    try:
        integrator = FletCliIntegrator(
            version=args.version,
            source_dir=args.source,
            output_dir=args.output,
        )
        return integrator.run(
            backup=not args.no_backup,
            verify=not args.no_verify,
        )
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
