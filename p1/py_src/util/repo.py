# -*- coding: utf-8-*-

from pathlib import Path
import os

root = Path(__file__).parent.parent.parent
src_root = os.path.join(root, "py_src")
res_root = os.path.join(root, "res")
config_root = os.path.join(src_root, "config")

if __name__ == "__main__":
    print(root)

