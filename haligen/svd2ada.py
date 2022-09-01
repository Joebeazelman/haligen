
import logging
import os
import typer
from pathlib import Path
from os_utils import execute_command, execute_subprocess, is_command_in_path_evironment


def is_svd2ada_installed(install_path: Path):
    logging.info("Checking if svd2ada is installed")

    svd2ada_dirname = execute_command(
        "alr get --dirname svd2ada")+"/bin/svd2ada"

    svd2ada_install_path = os.path.join(install_path, svd2ada_dirname)
    if svd2ada_install_path.exists():
        logging.info(
            f"SVD2ADA already installed in \"{svd2ada_install_path}\" from previous run.")
    elif not is_command_in_path_evironment("svd2ada"):
        logging.warn("Cannot find dependency SVD2ADA in PATH environment.")
        svd2ada_install_path = None

    return svd2ada_install_path


def ask_install_svd2ada(working_dir):
    user_response = typer.prompt(
        f"Would you like to exist, or install in the working directory (Install, Exit)?")
    return user_response


def install_svd2ada(install_path):
    execute_subprocess("alr get -b svd2ada", install_path)
    return install_path+"/bin/svd2ada"
