"""Postman Environment File execution Wrapper.

To use:

`postmanenv --envfile example.postman_environment.json test.py`
"""

import argparse
import json
import logging
from os import environ
from pathlib import Path

logger = logging.getLogger('postman_wrapper')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--envfile")
parser.add_argument("pythonfile")
args = parser.parse_args()


def execfile(filepath: str, globals=None, locals=None):
    """Execute a python file by path."""
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    logger.info("Loading %s with environment set from file.", filepath)
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)


def parse_environment(envfile: str):
    """Parse and load the Postman Environment Variables by path."""
    envfile_path = Path(envfile).resolve()
    logger.info("Loading '%s'", str(envfile_path))
    with open(envfile_path, "r", encoding="UTF-8") as file:
        loaded_file = json.loads(file.read())
    for environment_variables in loaded_file.get("values", []):
        if environment_variables["enabled"] is False:
            logger.warning(
                "Skipping '%s' as it's disabled.", environment_variables["key"])
            continue
        logger.info(
            "Setting '%s' in environment...", environment_variables["key"])
        environ[environment_variables["key"]] = environment_variables["value"]


def entrypoint():
    """Entrypoint for pip(x) install."""
    parse_environment(args.envfile)
    execfile(args.pythonfile)
