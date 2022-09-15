import logging
import os
from pathlib import Path
from os_utils import execute_subprocess, file_contains, insert_lines_into_file


def init_crate(crate_name: str, parent_path: Path):
    # initializes a crate in specified parent directory and returns path to crate's directory
    logging.info(
        f"Initializing crate \"{crate_name}\" at directory \"{parent_path}\".")
    execute_subprocess(f"alr init --lib {crate_name}", parent_path)
    return os.path.join(parent_path, crate_name)


def add_dependency_to_crate(crate: str, dependency: str, crate_path: Path) -> object:
    logging.info(
        f"Adding dependency {dependency} to crate \"{crate}\"")
    execute_subprocess(f"alr with {dependency}", crate_path)
    logging.info(f"Dependency \"{dependency}\" added.")
    return True


def configure_runtime(package_name: str, crate_path: Path, target: str, runtime: str):
    content = f"\tfor Target use \"{target}\";\n\tfor Runtime (\"Ada\") use \"{runtime}\";\n"
    crate_project_path = Path(crate_path, f"{package_name}.gpr")
    if is_runtime_configured(crate_project_path, content):
        return True

    logging.info(
        f'Configuring "{runtime}"runtime and "{target}" for "{package_name}" '
        f'in "{os.path.basename(crate_project_path)}."')

    insert_lines_into_file(crate_project_path,
                           2, content)
    return True


def is_runtime_configured(project_file_path: Path, content: str) -> bool:
    # if file already contains inserted lines, then return 0
    if file_contains(project_file_path, content):
        logging.info(
            f"New configuration has been inserted successfully into {os.path.basename(project_file_path)}.")
        return True
    else:
        logging.warning(
            "File has already been configured. Skipping configuration.")
    return False


def build_crate(crate_path: Path):
    logging.info(
        f"Building crate path \" {os.path.basename(crate_path)}.\"")
    execute_subprocess("alr build", crate_path)
    return True
