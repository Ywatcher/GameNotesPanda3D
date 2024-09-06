from pathlib import Path
import os

root = Path(__file__).parent.parent.parent
res_root = os.path.join(root, "res")


if __name__ == "__main__":
    print(root)

