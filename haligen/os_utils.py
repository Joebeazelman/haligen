# Draw spinner:
import json
import logging
from pathlib import Path
import shutil
from sre_constants import FAILURE
import subprocess
from progressbar import Progressbar, AdaptiveETA, SimpleProgress, Percentage, ETA


def execute_subprocess(cmd_and_args: str, current_working_dir: str):
    """Widgets that behave differently when length is unknown"""
    widgets = ['[When length is unknown at first]',
               ' Progress: ', SimpleProgress(),
               ', Percent: ', Percentage(),
               ' ', ETA(),
               ' ', AdaptiveETA()]
    bar = Progressbar(widgets=widgets, maxval=200)
    bar.start()

    # Execute some job with multiple lines on stdout:
    try:
        p = subprocess.Popen(cmd_and_args, cwd=current_working_dir, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if e.output.startswith('error: {'):
            print(e.output)
            error = json.loads(e.output[7:])  # Skip "error: "
            print(error['code'])
            print(error['message'])
            exit(FAILURE)

    # Lines will be collected in list:
    result = []

    # Until I get last line and the end of string:

    while p.stdout is not None:

        # Update spinner on one step:
        # It will update only when any line was printed to stdout!
        bar.update()
        # Read each line:

        line = p.stdout.readline()
        print(line.strip())

        # Add line in list and remove carriage return
        result.append(line.rstrip('\r'))

        # When no lines appears:
        if not line:
            print("\n")
            p.stdout.flush()
            break

    # Show finish message, it also useful because bar cannot start new line on console, why?
    print("Finish:")
    # Results as string:
    print(''.join(result))


def execute_command(command):
    try:
        result = subprocess.run(command, capture_output=True)

    except subprocess.CalledProcessError as e:
        if e.output.startswith('error: {'):
            error = json.loads(e.output[7:])  # Skip "error: "
            print(error['code'])
            print(error['message'])
            exit(FAILURE)
    return result


def is_command_in_path_evironment(command):
    logging.info("Checking if command is in PATH")
    command_path = shutil.which(command)
    return Path(command_path).exists()


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
