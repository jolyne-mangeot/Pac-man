
from setuptools import setup


with open("requirements.txt") as file:
    requirements: list[str] = file.read().splitlines()


setup(
    name="pacman",
    version="1.0.0",
    description="Pac-Man inspired Pygame team project "
    "as part of a learning course.",
    author="Belladone-Bzz, jolyne-mangeot",
    packages=["pacman", "pacman/models", "pacman/models/jsons"],
    install_requires=requirements,
)
