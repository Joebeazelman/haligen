# Draw spinner:
import json
import logging
from pathlib import Path
import shutil
from sre_constants import FAILURE
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
        p = subprocess.Popen(cmd_and_args, cwd=current_working_dir, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
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
        logging.info("Executing command: %s" % command)
        logging.info(f"Running command: {command.split(' ')}")
        result = subprocess.check_output(command.split(' ')).decode('utf-8')
        logging.info(result)
        return result

    except subprocess.CalledProcessError as e:
        if e.output.startswith('error: {'):
            error = json.loads(e.output[7:])  # Skip "error: "
            logging.error(error['code'])
            logging.error(error['message'])
            exit(-1)


def is_utility_in_path_var(utility):
    logging.info(
        f"Checking if utility \"{utility}\" is in PATH environment variable.")
    result = shutil.which(utility)
    if result is None:
        logging.info(
            f"\tUtility \"{utility}\" not found.")
    return Path(result) if result is not None else None


def file_contains(filename: str, content: str):
    with open(filename, 'r') as f:
        return content in f.read()


def insert_lines_into_file(file_name: str, line_index: int, content: str):
    with open(file_name, "r") as file:
        lines = file.readlines()

    # check if lines are already in the file
    if (lines[line_index] != content.splitlines()[0]):
        lines.insert(line_index, content)
    else:
        logging.warning(
            f"Cannot insert lines into file \"{file_name}\" at line {line_index}. Lines are already inserted.")

    with open(file_name, "w") as file:
        file.writelines(lines)
    return 0
