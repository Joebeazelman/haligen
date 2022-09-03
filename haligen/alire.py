import logging
import os
from pathlib import Path
from haligen.os_utils import execute_subprocess, file_contains, insert_lines_into_file


def init_crate(crate: str, parent_path: str):
    # initalizes a crate in specified parent directory and returns path to crate's directory
    logging.info(
        f"Initializing crate \"{crate}\" at directory \"{parent_path}\".")
    execute_subprocess(f"alr init --lib {crate}", parent_path)
    crate_dir = os.path.join(parent_path, crate)
    return crate_dir


def add_dependency_to_crate(crate, dependency: str, crate_path: Path):
    logging.info(
        f"Adding dependency {dependency} to crate \"{crate}\"")
    execute_subprocess(f"alr with {dependency}", crate_path)
    logging.info(f"Dependency \"{dependency}\" added.")
    return True


def configure_runtime(package_name, crate_path, target: str, runtime: str):
    content = f"\tfor Target use \"{target}\";\n\tfor Runtime (\"Ada\") use \"${runtime}\";\n"
    crate_proj_path = os.path.join(crate_path, package_name + ".gpr")
    if is_runtime_configured(crate_proj_path, content):
        return True

    logging.info(
        f"Configuring \"{runtime}\"runtime and \"{target}\" for \"{package_name}\" in \"{os.path.basename(crate_proj_path)}.\"")

    insert_lines_into_file(crate_proj_path,
                           2, content)
    return True


def is_runtime_configured(crate_proj_path, content):
    # if file already contains inserted lines, then return 0
    if not file_contains(crate_proj_path, content):
        logging.info(
            f"New configuration has been inserted successfully into {os.path.basename(crate_proj_path)}.")
        return True
    else:
        logging.info(
            f"File has already been configured. Skipping configuration.")
    return False


def build_crate(crate_path):
    logging.info(
        f"Building crate path \" {os.path.basename(crate_path)}.\"")
    execute_subprocess(f"alr build", crate_path)
    return True
