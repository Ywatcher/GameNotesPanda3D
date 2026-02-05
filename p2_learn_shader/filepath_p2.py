import os
import sys
from pathlib import Path

_filepath = Path(__file__)

sys.path.append(
    os.path.join(_filepath.parent.parent, "p1", "py_src")
)
