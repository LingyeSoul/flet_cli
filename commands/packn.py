import argparse
import os
import shutil
import sys
import uuid
from pathlib import Path

from flet.utils import is_macos, is_windows

import flet_cli.__pyinstaller.config as hook_config
from flet_cli.commands.base import BaseCommand
from flet_cli.__pyinstaller.utils import get_flet_bin_path, copy_flet_bin


class Command(BaseCommand):
    """
    Package Flet app to a desktop standalone bundle.
    """

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("script", type=str, help="path to a Python script")
        parser.add_argument(
            "-i",
            "--icon",
            dest="icon",
            help="path to an icon file (.ico, .png, .icns)",
        )
        parser.add_argument(
            "-n",
            "--name",
            dest="name",
            help="name for the generated executable (Windows) or app bundle (macOS)",
        )
        parser.add_argument(
            "--distpath",
            dest="distpath",
            help="where to put the bundled app (default: ./dist)",
        )
        parser.add_argument(
            "--onefile",
            dest="onefile",
            default=False,
            action="store_true",
            help="create a one-file bundled executable",
        )
        parser.add_argument(
            "--onedir",
            dest="onedir",
            default=False,
            action="store_true",
            help="create a one-folder bundle containing an executable (default)",
        )
        parser.add_argument(
            "--include-data-dir",
            dest="include_data_dir",
            action="append",
            nargs="*",
            help="additional data directory to be included in the executable",
        )
        parser.add_argument(
            "--product-name",
            dest="product_name",
            help="executable product name (Windows) or bundle name (macOS)",
        )
        parser.add_argument(
            "--file-description",
            dest="file_description",
            help="executable file description (Windows)",
        )
        parser.add_argument(
            "--product-version",
            dest="product_version",
            help="executable product version (Windows) or bundle version (macOS)",
        )
        parser.add_argument(
            "--copyright",
            dest="copyright",
            help="executable (Windows) or bundle (macOS) copyright",
        )
        parser.add_argument(
            "--bundle-id",
            dest="bundle_id",
            help="bundle identifier (macOS)",
        )
        parser.add_argument(
            "--debug-console",
            dest="debug_console",
            default=False,
            action="store_true",
            help="Show python console",
        )
        parser.add_argument(
            "-y",
            "--yes",
            dest="non_interactive",
            default=False,
            action="store_true",
            help="Non-interactive mode.",
        )
        parser.add_argument(
            "--nuitka-build-args",
            dest="nuitka_build_args",
            action="append",
            nargs="*",
            help="additional arguments for nuitka build command",
        )

    def handle(self, options: argparse.Namespace) -> None:
        from flet.utils.pip import ensure_flet_desktop_package_installed

        ensure_flet_desktop_package_installed()

        is_dir_not_empty = lambda dir: os.path.isdir(dir) and len(os.listdir(dir)) != 0

        # delete "build" directory
        build_dir = os.path.join(os.getcwd(), "build")
        if is_dir_not_empty(build_dir):
            if options.non_interactive:
                shutil.rmtree(build_dir, ignore_errors=True)
            else:
                delete_dir_prompt = input(
                    f'Do you want to delete "build" directory? (y/n) '
                )
                if not delete_dir_prompt.lower() == "n":
                    shutil.rmtree(build_dir, ignore_errors=True)
                else:
                    print('Failing... "build" directory must be empty to proceed.')
                    exit(1)

        # delete "dist" directory or DISTPATH directory
        # if --distpath cli option is specified
        if options.distpath:
            dist_dir = os.path.join(os.getcwd(), options.distpath)
        else:
            dist_dir = os.path.join(os.getcwd(), "dist")

        if is_dir_not_empty(dist_dir):
            if options.non_interactive:
                shutil.rmtree(dist_dir, ignore_errors=True)
            else:
                delete_dir_prompt = input(
                    f'Do you want to delete "{os.path.basename(dist_dir)}" directory? (y/n) '
                )
                if not delete_dir_prompt.lower() == "n":
                    shutil.rmtree(dist_dir, ignore_errors=True)
                else:
                    print(
                        f'Failing... DISTPATH "{os.path.basename(dist_dir)}" directory must be empty to proceed.'
                    )
                    exit(1)

        try:
            import subprocess

            from flet_cli.__pyinstaller.utils import copy_flet_bin

            # Create a custom temp directory structure similar to the reference code
            hook_config.temp_bin_dir = copy_flet_bin()
            print("临时Flet二进制目录:", hook_config.temp_bin_dir)

            if hook_config.temp_bin_dir is not None:
                # delete fletd/fletd.exe
                fletd_path = os.path.join(
                    hook_config.temp_bin_dir, "fletd.exe" if is_windows() else "fletd"
                )
                if os.path.exists(fletd_path):
                    os.remove(fletd_path)

                app_name = options.name or Path(options.script).stem
                icon_path = options.icon

                # Create .flet directory like in the example
                temp_path = str(Path(os.getcwd()).joinpath('.flet'))
                temp_bin_path = os.path.join(temp_path, 'bin')
                
                try:
                    # Create temp directories
                    os.makedirs(temp_path, exist_ok=True)
                    os.makedirs(temp_bin_path, exist_ok=True)
                    
                    # copy "bin" to temp
                    shutil.copytree(hook_config.temp_bin_dir, temp_bin_path, dirs_exist_ok=True)
                
                except Exception as e:
                    print(f"Error during flet.exe replacement: {e}")
                    raise
                
                # Set hook_config.temp_bin_dir to our temp directory
                hook_config.temp_bin_dir = temp_path
                
                print(f'temp dir: {hook_config.temp_bin_dir}')

                if is_windows():
                    # modify flet icon and info
                    exe_path = os.path.join(temp_bin_path, "flet", "flet.exe")
                    if os.path.exists(exe_path):
                        from flet_cli.__pyinstaller.win_utils import (
                            update_flet_view_icon,
                            update_flet_view_version_info,
                        )

                        # icon
                        if icon_path:
                            if not Path(icon_path).is_absolute():
                                icon_path = str(Path(os.getcwd()).joinpath(icon_path))
                            update_flet_view_icon(exe_path, icon_path)
                            print(f"Updated icon for {exe_path}")

                        # version info
                        if any([options.product_name, options.file_description, 
                               options.product_version, options.copyright]):
                            version_info_path = update_flet_view_version_info(
                                exe_path=exe_path,
                                product_name=options.product_name,
                                file_description=options.file_description,
                                product_version=options.product_version,
                                file_version=options.product_version,
                                company_name=None,
                                copyright=options.copyright,
                            )
                            print(f"Updated version info for {exe_path}")

                    # package, use modified flet app
                    nuitka_args = [sys.executable, "-m", "nuitka"]
                    
                    # Add mode based on onefile option
                    if options.onefile:
                        nuitka_args.append("--onefile")
                    else:
                        nuitka_args.append("--standalone")
                    
                    # Add script path
                    nuitka_args.append(options.script)
                    
                    # Add icon if specified
                    if options.icon:
                        icon_path = options.icon
                        if not Path(icon_path).is_absolute():
                            icon_path = str(Path(os.getcwd()).joinpath(icon_path))
                        nuitka_args.append('--windows-icon-from-ico=' + icon_path)
                    
                    # Add name if specified
                    if options.name:
                        nuitka_args.append('--output-filename=' + options.name)
                    
                    # Add output directory
                    output_dir = dist_dir
                    nuitka_args.append('--output-dir=' + output_dir)
                    
                    # Add jobs parameter to speed up compilation
                    nuitka_args.append('--jobs=8')
                    
                    # Add other options
                    nuitka_args.extend([
                        "--follow-imports",
                        "--nofollow-import-to=torch",
                        "--assume-yes-for-downloads",
                        "--mingw64"
                    ])
                    
                    # Add data directories if specified
                    if options.include_data_dir:
                        for include_data_arr in options.include_data_dir:
                            for include_data_item in include_data_arr:
                                nuitka_args.append('--include-data-dir=' + include_data_item)
                    
                    # Create flet_desktop structure with correct directory hierarchy
                    flet_desktop_path = os.path.join(temp_path, "flet_desktop")
                    flet_desktop_app_path = os.path.join(flet_desktop_path, "app")
                    os.makedirs(flet_desktop_app_path, exist_ok=True)
                    
                    # Copy the entire temp_bin_path to flet_desktop to preserve all files including exe and dll
                    if os.path.exists(temp_bin_path):
                        shutil.copytree(temp_bin_path, flet_desktop_app_path, dirs_exist_ok=True)
                        # Remove the temp_bin_path directory to avoid unnecessary bin folder in .flet
                        shutil.rmtree(temp_bin_path)
                    
                    # Add modified flet bin directory - mapping .flet to flet_desktop
                    print("Adding Flet binary directory mapping:", temp_path, "-> flet_desktop")
                    nuitka_args.append('--include-data-dir=' + flet_desktop_path + '=flet_desktop')
                    
                    # Add specific flet exe and dll files to ensure they are included
                    flet_exe_path = os.path.join(flet_desktop_app_path, "flet", "flet.exe")
                    if os.path.exists(flet_exe_path):
                        nuitka_args.append('--include-data-file=' + flet_exe_path + '=' + os.path.join("flet_desktop", "app", "flet", "flet.exe"))
                    
                    # Add critical DLL files explicitly
                    import glob
                    flet_dll_pattern = os.path.join(flet_desktop_app_path, "flet", "*.dll")
                    for dll_file in glob.glob(flet_dll_pattern):
                        dll_filename = os.path.basename(dll_file)
                        dest_path = os.path.join("flet_desktop", "app", "flet", dll_filename)
                        nuitka_args.append('--include-data-file=' + dll_file + '=' + dest_path)
                    
                    # Add .bin and .so files explicitly (including subdirectories)
                    flet_root_path = os.path.join(flet_desktop_app_path, "flet")
                    for extension in ["*.bin", "*.so"]:
                        # Find files in the root flet directory
                        for file_path in glob.glob(os.path.join(flet_root_path, extension)):
                            relative_path = os.path.relpath(file_path, flet_desktop_app_path)
                            dest_path = os.path.join("flet_desktop", "app", relative_path)
                            nuitka_args.append('--include-data-file=' + file_path + '=' + dest_path)
                        
                        # Find files in subdirectories recursively
                        for root, dirs, files in os.walk(flet_root_path):
                            for file in files:
                                if file.endswith((".bin", ".so")):
                                    file_path = os.path.join(root, file)
                                    relative_path = os.path.relpath(file_path, flet_desktop_app_path)
                                    dest_path = os.path.join("flet_desktop", "app", relative_path)
                                    nuitka_args.append('--include-data-file=' + file_path + '=' + dest_path)
                    
                    # Remove empty arguments
                    nuitka_args = [arg for arg in nuitka_args if arg]
                    
                    # Add Windows specific options
                    file_description = options.file_description or "Flet App"
                    nuitka_args.append('--file-description=' + file_description)
                    
                    copyright_text = options.copyright or "Copyright (c) " + app_name
                    nuitka_args.append('--copyright=' + copyright_text)
                    
                    product_version = options.product_version or "1.0.0"
                    nuitka_args.append('--product-version=' + product_version)
                    
                    product_name = options.product_name or app_name
                    nuitka_args.append('--product-name=' + product_name)
                    
                    # Add additional build arguments if provided
                    if options.nuitka_build_args:
                        for nuitka_build_arg_arr in options.nuitka_build_args:
                            nuitka_args.extend(nuitka_build_arg_arr)
                    
                    # Add console option
                    if options.debug_console:
                        nuitka_args.append("--windows-console-mode=force")
                    else:
                        nuitka_args.append("--windows-console-mode=disable")
                
                    # run Nuitka!
                    print("Running Nuitka:", nuitka_args)
                    result = subprocess.run(nuitka_args)
                    
                    
                    if result.returncode != 0:
                        print("Nuitka compilation failed!")
                        sys.exit(1)
                
                    # cleanup temp path
                    if temp_path is not None and os.path.exists(temp_path):
                        print("Deleting temp directory:", temp_path)
                        shutil.rmtree(temp_path, ignore_errors=True)
                            
        except ImportError as e:
            print("Please install Nuitka module to use flet packn command:", e)
            sys.exit(1)