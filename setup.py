from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="LLMOPS-3",
    version="0.1",
    author="Taiwo Sokunbi",
    author_email="sokunbitaiwo82@gmail.com",
    description="LLMOPS-3 is a project that uses LLMs to perform operations",
    url="https://github.com/andela-Taiwo/study-buddy",
    packages=find_packages(),
    install_requires = requirements,
)