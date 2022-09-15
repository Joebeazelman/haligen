# Draw spinner:
import json
import logging
import os
import pathlib
from pathlib import Path
import shutil
import subprocess
from progressbar import ProgressBar, AdaptiveETA, SimpleProgress, Percentage, ETA


def execute_subprocess(cmd_and_args: str, current_working_dir: Path):
    """Widgets that behave differently when length is unknown"""
    widgets = ['[When length is unknown at first]',
               ' Progress: ', SimpleProgress(),
               ', Percent: ', Percentage(),
               ' ', ETA(),
               ' ', AdaptiveETA()]
    bar = ProgressBar(widgets=widgets, maxval=200)
    bar.start()

    # Execute some job with multiple lines on stdout:
    try:
        p = subprocess.Popen(cmd_and_args, cwd=current_working_dir, shell=False, universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if e.output.startswith('error: {'):
            logging.error(e.output)
            error = json.loads(e.output[7:])  # Skip "error: "
            logging.error(error['code'])
            logging.error(error['message'])
            exit(-1)

    # Lines will be collected in list:
    result = []

    # Until I get last line and the end of string:

    while p.stdout is not None:

        # Update spinner on one step:
        # It will update only when any line was printed to stdout!
        bar.update()
        # Read each line:

        line = p.stdout.readline()
        logging.info(line.strip())

        # Add line in list and remove carriage return
        result.append(line.rstrip('\r'))

        # When no lines appears:
        if not line:
            logging.info("\n")
            p.stdout.flush()
            break

    # Show finish message, it also useful because bar cannot start new line on console, why?
    logging.error("Finish:")
    # Results as string:
    logging.error(''.join(result))


def execute_command(command):
    try:
        logging.info("\t\tExecuting command: %s" % command)
        result = subprocess.check_output(command.split(' ')).decode('utf-8')
        return result

    except subprocess.CalledProcessError as e:
        if e.output.startswith('error: {'):
            error = json.loads(e.output[7:])  # Skip "error: "
            logging.error(error['code'])
            logging.error(error['message'])
            exit(-1)


def is_utility_in_path_var(utility: pathlib.Path) -> Path:
    logging.info(
        f"\t\tChecking if utility \"{utility}\" is in PATH environment variable.")
    result = shutil.which(utility)
    if result is None:
        try:
            os.stat(result)
        except OSError as e:
            logging.error(
                f"\t\t\tUtility \"{utility}\" not found in PATH.")
    return Path(result) if result is not None else None


def file_contains(filename: str, content: str):
    try:
        with open(filename, 'r') as f:
            return content in f.read()
    except IOError as e:
        logging.error("Error reading file \"{filename}\". Error: {e}")
        exit(-1)


def insert_lines_into_file(file_path: str, line_index: int, content: str):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except IOError as e:
        logging.error(
            f"Error reading file \"{os.path.basename(file_path)}\". Error: {e}")
        exit(-1)

    # check if lines are already in the file
    if (lines[line_index] != content.splitlines()[0]):
        lines.insert(line_index, content)

        logging.warning(
            f"\t\tCannot insert lines into file \"{os.path.basename(file_path)}\" at line {line_index}. Lines are already inserted.")
    try:
        with open(file_path, "w") as file:
            file.writelines(lines)
    except IOError as e:
        logging.error(
            f"Error writing file \"{os.path.basename(file_path)}\". Error: {e}")
        exit(-1)

    return True


def normalize_path(path):
    return os.path.normpath(path)
