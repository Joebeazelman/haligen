import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Optional
import typer
from haligen.alire import build_crate, configure_runtime, init_crate
from haligen.svd2ada import ask_install_svd2ada, generate_ada_from_svd, install_svd2ada, is_svd2ada_installed

logging.basicConfig(level=logging.INFO)
app = typer.Typer()
app_root = Path(typer.get_app_dir("haligen"))
app_workingdir = Path(os.getcwd())
app_temp_tooldir = Path.joinpath(app_root, "tmp_install")


def version_callback(value: bool):
    if value:
        print(f"Version 0.1.0")
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
             package_name: Optional[bool] = typer.Option(
             None, "--package_name", help="Package name (defaults to name of svd file)"),
             version: Optional[bool] = typer.Option(
             None, "--version", "-v", callback=version_callback, help="Displays version information", is_eager=True),
             force: bool = typer.Option(False, "--force", "-f", confirmation_prompt=True, help="Overwrite existing output files", show_default=True)):
    """
    Code generator for Hardware Abstraction layer (HAL) in Ada from
    an SVD hardware specification file.
    """
    working_dir = app_workingdir

    logging.info(f"Starting tool from directory: {working_dir}")
    svd2ada_executable_path = None

    if (package_name == None):
        package_name = Path(svd_filepath).stem.lower()
        logging.info(f"\"{package_name}\" is chosen as the package name.")

    # check if svd2ada is available, if not ask user if they want to install it
    if (svd2ada_executable_path := is_svd2ada_installed(app_temp_tooldir)) is None:
        if (ask_install_svd2ada()):
            app_temp_tooldir.mkdir(parents=True, exist_ok=True)
            svd2ada_executable_path = install_svd2ada(app_temp_tooldir)
        else:
            logging.info("User chose not to install Svd2Ada. Exiting.")
            exit(0)

    crate_path = init_crate(output_dir, "gnat_arm_elf")
    # TODO: make runtime and target selectable
    if generate_ada_from_svd(svd2ada_executable_path, svd_filepath, crate_path, package_name):
        build_crate(crate_path)

    # build crate

   # print(svd2ada_path)
