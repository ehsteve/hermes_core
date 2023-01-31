# see license/LICENSE.rst
import os.path

try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

from hermes_core.util.config import load_config, print_config
from hermes_core.util.logger import _init_log

# Load user configuration
config = load_config()

log = _init_log(config=config)

# Then you can be explicit to control what ends up in the namespace,
__all__ = ["config", "print_config"]

MISSION_NAME = "hermes"
INST_NAMES = ["eea", "nemisis", "merit", "spani", "sunsensor"]
INST_SHORTNAMES = ["eea", "nms", "mrt", "spn", "ss"]
INST_TARGETNAMES = ["EEA", "MAG", "MERIT", "SPANI", "SS"]
INST_TO_SHORTNAME = dict(zip(INST_NAMES, INST_SHORTNAMES))
INST_TO_TARGETNAME = dict(zip(INST_NAMES, INST_TARGETNAMES))

_package_directory = os.path.dirname(os.path.abspath(__file__))
_data_directory = os.path.abspath(os.path.join(_package_directory, "data"))

# log.info(f"hermes_core version: {__version__}")
