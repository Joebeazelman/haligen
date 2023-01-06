
import logging
from pathlib import Path

import xml.etree.ElementTree as xml_doc

from os_utils import execute_command, execute_subprocess, is_utility_in_path_var


def is_svd2ada_installed(install_path: Path):
    logging.info("\tGetting svd2ada directory name from Alire")

    # first check if SVD2ADA is installed and in PATH environment or installed from previous run
    # return the full path to the svd2ada installation directory
    utility = "svd2ada"
    svd2ada_dirname = execute_command(f"alr get --dirname {utility}").strip()
    utility_path = install_path.joinpath(svd2ada_dirname)
    logging.info(f"\tChecking if svd2ada is installed in \"{utility_path}\"")
    if Path.is_dir(utility_path):
        logging.info(
            f"\t\tSVD2ADA already installed in \"{utility_path}\" from previous run.")
    elif (utility_path := is_utility_in_path_var(utility)):
        logging.info(
            f"\t\tUtility \"{utility}\" already exists PATH environment and located at \"{utility_path}\".")

    return utility_path.joinpath("bin", "svd2ada") if utility_path is not None else None


def ask_install_svd2ada():
    return typer.prompt(f"\tWould you like to install to temporarily install it or exit (Yes, or No)?")


def install_svd2ada(install_path):
    logging.info(f"\tInstalling SVD2ADA in {install_path}")

    # first check if SVD2ADA is installed and in PATH environment or installed from previous run
    # return the full path to the installation directory
    execute_subprocess("alr get -b svd2ada", install_path)
    return f"{install_path}/bin/svd2ada"


def generate_ada_from_svd(svd2ada_executable_path, svd_filepath, crate_path, svd_package_name):
    command = f"\"{svd2ada_executable_path}\" \"{svd_filepath}\" --boolean -o \"{crate_path}/src/{svd_package_name}\" -p {svd_package_name} --base-types-package HAL --gen-uint-always"
    logging.info(
        f"\tExecuting command:\n\t\"{command}\"")
    execute_subprocess(command, crate_path)
    return True
