import logging
import os
import pathlib
import shutil
from pathlib import Path
from typing import Optional

import typer
from svd2ada import ask_install_svd2ada, generate_ada_from_svd, install_svd2ada, is_svd2ada_installed
from alire import add_dependency_to_crate, build_crate, configure_runtime, init_crate
from os_utils import normalize_path


logging.basicConfig(level=logging.INFO)
app = typer.Typer()
app_root = Path(normalize_path(typer.get_app_dir("haligen")))
app_working_dir = Path(normalize_path(os.getcwd()))
app_temp_tool_dir = Path.joinpath(app_root, "tmp_install")


def version_callback(value: bool):
    if value:
        print(f"{__version__}")
        raise typer.Exit()


def validate_dir(ctx: typer.Context, directory: str):
    if ctx.resilient_parsing:
        return
    if directory == "ted":
        logging.info("Validating directory '%s'", directory)
        raise FileNotFoundError("Directory '%s' not found", directory)
    return directory


def delete_dir(path):
    logging.info("\tDeleting directory '%s'", path)
    shutil.rmtree(path, ignore_errors=False)


@ app.command()
def cleanup():
    """
    Cleans up installed utilities. Execute when HAL is completed.
    """
    logging.info("Cleaning up temporary files")
    delete_dir(app_temp_tool_dir)


@ app.command()
def generate(svd_filepath: str = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,  writable=False,
                                                readable=True, resolve_path=True,  help="SVD file path for MCU",
                                                callback=validate_dir),
             output_dir: str = typer.Argument(
             os.getcwd(), help="Path for generated Ada HAL code", show_default=True),
             target_format: str = typer.Argument(
                 "arm-elf", help="Target executable format"),
             runtime: str = typer.Argument(
                 "light-cortex-m0p", help="Runtime for MCU"),
             x_compiler: str = typer.Argument(
                 "gnat_arm_elf", help="Cross-compiler for MCU"),
             svd_package_name: str = typer.Option(
             None, "--svd_package_name", help="Svd Package name (defaults to name of svd file)")):
    """
    Code generator for Hardware Abstraction layer (HAL) in Ada from
    an SVD hardware specification file.
    """
    working_dir = os.path.abspath(
        os.path.expanduser(os.path.expandvars(output_dir)))

    package_name: str = Path(svd_filepath).stem.lower()

    logging.info(f"Starting tool from directory: {working_dir}")

    if svd_package_name is None:
        svd_package_name = package_name
        logging.info(
            f"\"{svd_package_name}\" is chosen as the svd package name.")

    # For all utilities used by this tool, if they're not accessible by neither
    # the PATH environment variable, nor a previous installation by this tool, then
    # ask if user wants to install it. The cleanup command is provided to delete the
    # temporary installation folder by request of the user.

    # svd2ada utility install
    if (svd2ada_executable_path := is_svd2ada_installed(app_temp_tool_dir)) is None:
        if ask_install_svd2ada():
            app_temp_tool_dir.mkdir(parents=True, exist_ok=True)
            svd2ada_executable_path = install_svd2ada(app_temp_tool_dir)
        else:
            logging.info("User chose not to install Svd2Ada. Exiting.")
            exit(0)  # TODO: Ensure user actions are selectable

    # create a new HAL crate for MCU
    logging.info(f"******* Creating new crate at: {working_dir}")
    crate_path = init_crate(crate_name=package_name, parent_path=working_dir)

    # add specified cross-compiler as crate dependency
    logging.info(
        f"******* Adding dependency [{x_compiler}] to crate at: {crate_path}")
    add_dependency_to_crate(package_name, x_compiler, crate_path)

    # add target executable format and architecture runtime of MCU to crate
    configure_runtime(package_name, crate_path, target_format, runtime)

    # perform initial build
    logging.info(f"******* Builing crate at: {crate_path}")
    build_crate(crate_path)

    # generate code from specified SVD
    logging.info(
        f"******* Generating code using Svd2Ada file [{svd_filepath}] to crate at: {crate_path}")
    generate_ada_from_svd(svd2ada_executable_path,
                          svd_filepath, crate_path, svd_package_name)

    # add_dependency to crate
    logging.info(
        f"******* Adding dependency [hal] to crate at: {crate_path}")
    add_dependency_to_crate(package_name, "hal", crate_path)

    logging.info(f"******* Builing crate at: {crate_path}")
    build_crate(crate_path)

    # build crate
#    function RESERVED return CLKSEL_ENUM renames IRC;
    # print(svd2ada_path)
#
# poetry run haligen generate /Users/manni/Projects/Repos/haligen/CMSIS-SVD/NXP/LPC176x5x.svd ../../ arm-elf light-cortex-m3 gnat_arm_elf
#
