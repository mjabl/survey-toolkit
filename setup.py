# pylint: disable=missing-docstring,invalid-name
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="survey-toolkit",
    version="0.1.0",
    author="mjabl",
    description="Toolkit for survey data extraction and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas>=0.24", "many_stop_words>=0.2"],
    python_requires='>=3.6',
)
