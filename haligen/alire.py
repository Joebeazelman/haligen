import logging
import os
from haligen.os_utils import execute_subprocess, file_contains, insert_lines_into_file


def init_crate(crate_name: str, x_compiler_name: str):
    current_dir = os.getcwd()
    logging.info(
        f"Initializing crate \"{crate_name}\" at directory \"{current_dir}\"")
    execute_subprocess(f"alr init --lib {crate_name}", current_dir)
    crate_dir = os.path.join(current_dir, crate_name)
    logging.info(
        f"Configuring {x_compiler_name} compiler for   crate \"{crate_name}\" at directory \"{crate_dir}\"")
    execute_subprocess(f"alr with {x_compiler_name}", crate_dir)
    return crate_dir


def configure_runtime(package_name, crate_path, target: str, runtime: str):
    content = f"\tfor Target use \"{target}\";\n\tfor Runtime (\"Ada\") use \"${runtime}\";\n"
    logging.info(
        f"Configuring \"{runtime}\"runtime and \"{target}\" for \"{package_name}\" in \"{os.path.basename(crate_path)}\"")
    crate_path = os.path.join(crate_path, package_name + ".gpr")
    insert_lines_into_file(crate_path,
                           2, content)

    return 0


def is_runtime_configured(crate_path, content):
    # if file already contains inserted lines, then return 0
    if not file_contains(crate_path, content):
        logging.info(
            f"New configuration has been inserted successfully into {os.path.basename(crate_path)}.")
        return True
    else:
        logging.info(
            f"File has already been configured. Skipping configuration.")
    return False


def build_crate(crate_path):
    logging.info(
        f"Building crate path \" {os.path.basename(crate_path)}\".")
    execute_subprocess(f"alr build", crate_path)
    return 0
