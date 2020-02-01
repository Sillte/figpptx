from pathlib import Path
from setuptools import setup
from setuptools import setup, find_packages
from devs.mycommand import SpaceRemoverCommand
from devs.mycommand import FormatterCommand

_this_folder = Path(__file__).resolve().parent


def _read_requirements(path):
    return [line for line in map(str.strip, Path(path).read_text().split("\n")) if line]


_install_requires = _read_requirements(_this_folder / "requirements.txt")
_dev_requires = _read_requirements(_this_folder / "devs/dev_requirements.txt")

if __name__ == "__main__":
    setup(
        packages=find_packages(),
        install_requires=_install_requires,
        setup_requires = _dev_requires,
        cmdclass={"remove_space": FormatterCommand, "format": FormatterCommand},
    )
