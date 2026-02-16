import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("artifacts/figures"))
    parser.add_argument("--dst", type=Path, default=Path("paper/figures"))
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    src = args.src
    dst = args.dst
    dst.mkdir(parents=True, exist_ok=True)

    if args.clean:
        for path in dst.glob("*.png"):
            path.unlink()

    files = sorted(src.glob("*.png"))
    copied = []
    for path in files:
        target = dst / path.name
        shutil.copy2(path, target)
        copied.append(path.name)

    print(f"copied {len(copied)} files")
    if copied:
        print("files:")
        for name in copied:
            print(name)


if __name__ == "__main__":
    main()
