import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Optional
import typer
import haligen
from haligen.alire import add_dependency_to_crate, build_crate, configure_runtime, init_crate
from haligen.os_utils import normalize_path
from haligen.svd2ada import ask_install_svd2ada, generate_ada_from_svd, install_svd2ada, is_svd2ada_installed

logging.basicConfig(level=logging.INFO)
app = typer.Typer()
app_root = Path(normalize_path(typer.get_app_dir("haligen")))
app_workingdir = Path(normalize_path(os.getcwd()))
app_temp_tooldir = Path.joinpath(app_root, "tmp_install")


def version_callback(value: bool):
    if value:
        print(f"{haligen.__version__}")
        raise typer.Exit()


def validate_dir(ctx: typer.Context, dir: str):
    if ctx.resilient_parsing:
        return
    if dir == "ted":
        logging.info("Validating directory '%s'", dir)
        raise FileNotFoundError("Directory '%s' not found", dir)
    return dir


def delete_dir(path):
    logging.info("\tDeleting directory '%s'", path)
    shutil.rmtree(path, ignore_errors=False)


@ app.command()
def cleanup():
    """
    Cleans up installed utilities. Excute when HAL is completed.
    """
    logging.info("Cleaning up temporary files")
    delete_dir(app_temp_tooldir)


@ app.command()
def generate(svd_filepath: str = typer.Argument(..., exists=True, file_okay=True, dir_okay=False,  writable=False, readable=True, resolve_path=True,  help="SVD file path for MCU", callback=validate_dir),
             output_dir: str = typer.Argument(
             os.getcwd(), help="Path for generated Ada HAL code", show_default=True),
             target_format: str = typer.Argument(
                 "arm-elf", help="Target executable format"),
             runtime: str = typer.Argument(
                 "zfp-cortex-m0p", help="Runtime for MCU"),
             x_compiler: str = typer.Argument(
                 "gnat_arm_elf", help="Cross-compiler for MCU"),
             package_name: Optional[bool] = typer.Option(
             None, "--package_name", help="Package name (defaults to name of svd file)"),
             version: Optional[bool] = typer.Option(
             None, "--version", "-v", callback=version_callback, help="Displays version information", is_eager=True),
             force: bool = typer.Option(False, "--force", "-f", confirmation_prompt=True, help="Overwrite existing output files", show_default=True)):
    """
    Code generator for Hardware Abstraction layer (HAL) in Ada from
    an SVD hardware specification file.
    """
    working_dir = output_dir

    logging.info(f"Starting tool from directory: {working_dir}")
    svd2ada_executable_path = None

    if (package_name == None):
        package_name = Path(svd_filepath).stem.lower()
        logging.info(f"\"{package_name}\" is chosen as the package name.")

    # For all utilties used by this tool, if they're not accessible by neither
    # the PATH environment variable, nor a previous installation by this tool, then
    # ask if user want to install it. The cleanup command is provided to delete the
    # temporary installation folder by request of the user.

    # svd2ada utility install
    if (svd2ada_executable_path := is_svd2ada_installed(app_temp_tooldir)) is None:
        if (ask_install_svd2ada()):
            app_temp_tooldir.mkdir(parents=True, exist_ok=True)
            svd2ada_executable_path = install_svd2ada(app_temp_tooldir)
        else:
            logging.info("User chose not to install Svd2Ada. Exiting.")
            exit(0)  # TODO: Ensure user actios are selectable

    # create a new HAL crate for MCU
    crate_path = init_crate(crate=package_name, parent_path=working_dir)

    # add specified cross-compiler as crate dependency
    add_dependency_to_crate(package_name, x_compiler, crate_path)

    # add target executable format and architecture runtime of MCU to crate
    # TODO: make runtime and target selectable
    configure_runtime(package_name, crate_path, target_format, runtime)

    # perform initial build
    build_crate(crate_path)

    generate_ada_from_svd(svd2ada_executable_path,
                          svd_filepath, crate_path, package_name)
    add_dependency_to_crate(package_name, "hal", crate_path)
    build_crate(crate_path)

    # build crate

   # print(svd2ada_path)
