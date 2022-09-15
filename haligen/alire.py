import logging
import os
from pathlib import Path
from haligen.os_utils import execute_subprocess, file_contains, insert_lines_into_file
from logdecorator import log_on_start, log_on_end, log_on_error, log_exception


@log_on_start(logging.INFO, "Initializing crate \"{crate:s}\" in directory \"{parent_path}\".")
@log_on_error(logging.ERROR, "Error initializing crate \"{crate:s}\": {e!r}",
              on_exceptions=IOError,
              reraise=True)
@log_on_end(logging.INFO, "Crate initialized.")
def init_crate(crate: str, parent_path: str):
    ''' initalizes a crate in specified parent directory and returns path to crate's directory'''
    execute_subprocess(f"alr init --lib {crate}", parent_path)
    crate_dir = os.path.join(parent_path, crate)
    return crate_dir


@log_on_start(logging.DEBUG, "Adding dependency \"{dependency}\" to crate \"{crate}\"")
@log_on_error(logging.ERROR, "Error initializing crate \"{crate:s}\": {e!r}",
              on_exceptions=IOError,
              reraise=True)
@log_on_end(logging.DEBUG, "Dependency added.")
def add_dependency_to_crate(crate, dependency: str, crate_path: Path):
    execute_subprocess(f"alr with {dependency}", crate_path)
    return True


@log_on_start(logging.DEBUG, "Configuring \"{runtime}\"runtime and \"{target}\" for \"{package_name}\".")
@log_on_error(logging.ERROR, "Error configuring runtime and target: {e!r}",
              on_exceptions=IOError,
              reraise=True)
@log_on_end(logging.DEBUG, "Runtime configured.")
def configure_runtime(package_name: str, crate_path, target: str, runtime: str):
    ''' Add runtime and target configuration to project file'''
    content = f"\tfor Target use \"{target}\";\n\tfor Runtime (\"Ada\") use \"{runtime}\";\n"
    crate_proj_path = os.path.join(crate_path, package_name + ".gpr")
    if is_runtime_configured(crate_proj_path, content):
        insert_lines_into_file(crate_proj_path, 2, "--")
        insert_lines_into_file(crate_proj_path, 3, "--")

    insert_lines_into_file(crate_proj_path, 2, content)

    return True


@log_on_start(logging.DEBUG, "Building crate path \"{crate_path}.\"")
@log_on_error(logging.ERROR, "Error configuring runtime and target: {e!r}",
              on_exceptions=IOError,
              reraise=True)
@log_on_end(logging.DEBUG, "Project build completed.")
def build_crate(crate_path):
    execute_subprocess(f"alr build", crate_path)
    return True


def is_runtime_configured(crate_proj_path, content):
    # if file already contains inserted lines, then return 0
    if file_contains(crate_proj_path, "for Runtime use"):
        return True

    return False
