import logging
import os
from pathlib import Path
import shutil
from typing import Optional
import typer
from haligen.alire import ask_install_svd2ada, build_crate, init_crate, install_svd2ada, is_svd2ada_installed, validate_dir, configure_runtime

logging.basicConfig(level=logging.INFO)
app = typer.Typer()
app_root = typer.get_app_dir("haligen")


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


@app.command()
def cleanup(app_dir):
    """
    Cleans up installed utilities. Excute when HAL is completed.
    """
    logging.info("Cleaning up temporary files")
    shutil.rmtree(os.path.join(app_dir, "tmp"), ignore_errors=True)


@app.command()
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
    working_dir = os.getcwd()
    logging.info(f"Starting tool from directory: {working_dir}")

    if (package_name == None):
        package_name = Path(svd_filepath).stem.lower()
        logging.info("\"{package_name}\" is chosen as the package name.")

    # check if svd2ada is available, if not ask user if they want to install it
    if is_svd2ada_installed(working_dir) != None:
        install_svd2ada(working_dir)
    elif (ask_install_svd2ada(working_dir)):
        svd2ada_path = install_svd2ada(working_dir)
    else:
        logging.info("User chose not to install Svd2Ada. Exiting.")
        exit(0)

    svd2ada_path = install_svd2ada(working_dir)
    crate_path = init_crate(package_name, "gnat_arm_elf")
    # TODO: make runtime and target selectable
    configure_runtime(package_name, crate_path, "test runtime", "test target")
    # generate_svd2ada(svd_filepath, crate_path, package_name, svd2ada_path)

    # build crate
    build_crate(crate_path)
    print(svd2ada_path)
