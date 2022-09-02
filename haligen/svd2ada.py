
import logging
import os
import typer
from pathlib import Path

import xml.etree.ElementTree as xml_doc

from haligen.os_utils import execute_command, execute_subprocess, is_utility_in_path_var


def is_svd2ada_installed(install_path: Path):
    logging.info("Checking if svd2ada is installed")

    # first check if SVD2ADA is installed and in PATH environment or installed from previous run
    # return the full path to the svd2ada installation directory
    utility = "svd2ada"
    svd2ada_dirname = execute_command(f"alr get --dirname {utility}")
    utility_path = install_path.joinpath(svd2ada_dirname)
    if utility_path.exists():
        logging.info(
            f"SVD2ADA already installed in \"{utility_path}\" from previous run.")
    elif (utility_path := is_utility_in_path_var(utility)):
        logging.info(
            f"Utility \"{utility}\" already exists PATH environment and located at \"{utility_path}\".")

    return utility_path


def ask_install_svd2ada():
    user_response = typer.prompt(
        f"Would you like to install to temporarily install it or exit (Yes, or No)?")
    return user_response


def install_svd2ada(install_path):
    execute_subprocess("alr get -b svd2ada", install_path)
    return install_path+"/bin/svd2ada"


def generate_ada_from_svd(svd2ada_executable_path, svd_filepath, crate_path, package_name):
    command = f"{svd2ada_executable_path} {svd_filepath} --boolean -o {crate_path}/src -p {package_name} --base-types-package HAL --gen-uint-always"
    logging.info(
        f"Executing command:\n\t\"{command}\"")
    execute_subprocess(command, crate_path)
    return True
